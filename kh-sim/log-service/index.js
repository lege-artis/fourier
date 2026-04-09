/**
 * kh-sim-log-service  --  KH-SIM simulation event recorder + viewer API
 * Project : VibeCodeProjects / kh-sim   |  Task: KH-014
 * Port    : 8006
 *
 * Architecture
 * ------------
 * Passive log sink -- backends or the React frontend POST simulation events
 * here; the service persists them to MongoDB vibedev.logs and makes them
 * available via a viewer API so per-backend React pages (KH-008..012) can
 * render live simulation history without coupling backends to the log store.
 *
 * Routes
 * ------
 *   POST /event            Record a simulation event
 *   GET  /viewer           Query simulation log entries
 *   GET  /summary          Per-backend aggregate stats
 *   GET  /health           Service + MongoDB connectivity probe
 *
 * Environment variables
 * ----------------------
 *   PORT         Server port (default: 8006)
 *   MONGO_URI    MongoDB connection string (default: mongodb://localhost:27017)
 *   MONGO_DB     Database name (default: vibedev)
 *   MONGO_COLL   Collection name (default: logs)
 *   LOG_LEVEL    Winston level (default: info)
 */

'use strict';

const express   = require('express');
const { MongoClient, ObjectId } = require('mongodb');
const winston   = require('winston');
const os        = require('os');

// ── Configuration ─────────────────────────────────────────────────────────────
const PORT       = parseInt(process.env.PORT       || '8006', 10);
const MONGO_URI  = process.env.MONGO_URI  || 'mongodb://localhost:27017';
const MONGO_DB   = process.env.MONGO_DB   || 'vibedev';
const MONGO_COLL = process.env.MONGO_COLL || 'logs';
const LOG_LEVEL  = process.env.LOG_LEVEL  || 'info';

// ── Logger (internal service logger, not simulation events) ───────────────────
const logger = winston.createLogger({
  level: LOG_LEVEL,
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.printf(({ timestamp, level, message, ...meta }) => {
      const m = Object.keys(meta).length ? ' ' + JSON.stringify(meta) : '';
      return `${timestamp} [${level.toUpperCase()}] ${message}${m}`;
    })
  ),
  transports: [new winston.transports.Console()],
});

// ── MongoDB ───────────────────────────────────────────────────────────────────
let mongoClient = null;
let db          = null;

async function connectMongo() {
  try {
    mongoClient = new MongoClient(MONGO_URI, {
      connectTimeoutMS: 3000,
      serverSelectionTimeoutMS: 3000,
    });
    await mongoClient.connect();
    db = mongoClient.db(MONGO_DB);
    // Ensure TTL index exists (30-day retention, consistent with LOG-006)
    const coll = db.collection(MONGO_COLL);
    await coll.createIndex(
      { '@timestamp': 1 },
      { expireAfterSeconds: 2592000, background: true }  // 30 days
    );
    logger.info('MongoDB connected', { uri: MONGO_URI, db: MONGO_DB, collection: MONGO_COLL });
    return true;
  } catch (err) {
    logger.warn('MongoDB unavailable at startup -- service running degraded', { err: err.message });
    return false;
  }
}

function collection() {
  if (!db) throw new Error('MongoDB not connected');
  return db.collection(MONGO_COLL);
}

// ── Request validation ────────────────────────────────────────────────────────
const VALID_BACKENDS = new Set([
  'kh-rust', 'kh-scala', 'kh-cpp', 'kh-fortran', 'kh-pascal',
]);

function validateEventBody(body) {
  const errors = [];
  if (!body.backend)              errors.push('backend is required');
  if (body.backend && !VALID_BACKENDS.has(body.backend))
    errors.push(`backend must be one of: ${[...VALID_BACKENDS].join(', ')}`);
  if (body.steps_completed !== undefined && typeof body.steps_completed !== 'number')
    errors.push('steps_completed must be a number');
  if (body.compute_ms !== undefined && typeof body.compute_ms !== 'number')
    errors.push('compute_ms must be a number');
  return errors;
}

// ── Express app ───────────────────────────────────────────────────────────────
const app = express();
app.use(express.json({ limit: '2mb' }));

// Request logger middleware
app.use((req, _res, next) => {
  logger.info(`${req.method} ${req.path}`, { ip: req.ip });
  next();
});

// ── POST /event ───────────────────────────────────────────────────────────────
/**
 * Record a simulation event.
 *
 * Body schema:
 *   backend          string   required  e.g. "kh-rust"
 *   session_id       string   optional  caller session identifier
 *   steps_completed  number   optional  simulation steps run
 *   t_final          number   optional  simulation time at end
 *   compute_ms       number   optional  wall-clock time for simulation
 *   params           object   optional  simulation request parameters
 *   diagnostics      object   optional  physics diagnostics (ke, enstrophy, etc.)
 *   status           string   optional  "ok" | "error" (default "ok")
 *   error_detail     string   optional  error description if status="error"
 */
app.post('/event', async (req, res) => {
  const errors = validateEventBody(req.body);
  if (errors.length) {
    return res.status(400).json({ error: 'Validation failed', details: errors });
  }

  const {
    backend,
    session_id    = 'none',
    steps_completed,
    t_final,
    compute_ms,
    params        = {},
    diagnostics   = {},
    status        = 'ok',
    error_detail,
  } = req.body;

  const doc = {
    '@timestamp':      new Date().toISOString(),
    source:            'kh-sim-log-service',
    app:               backend,
    session_id,
    message:           `simulation ${status}`,
    level:             status === 'error' ? 'error' : 'info',
    metadata: {
      host:    os.hostname(),
      pid:     process.pid,
      env:     process.env.NODE_ENV || 'development',
      version: '1.0.0',
    },
    context: {
      backend,
      steps_completed,
      t_final,
      compute_ms,
      params,
      diagnostics,
      status,
      ...(error_detail ? { error_detail } : {}),
    },
  };

  try {
    const result = await collection().insertOne(doc);
    logger.info('Event recorded', { backend, id: result.insertedId });
    return res.status(201).json({ id: result.insertedId, status: 'recorded' });
  } catch (err) {
    logger.error('Event insert failed', { err: err.message });
    return res.status(503).json({ error: 'Log storage unavailable', detail: err.message });
  }
});

// ── GET /viewer ───────────────────────────────────────────────────────────────
/**
 * Query simulation log entries.
 *
 * Query params:
 *   backend     string   optional  filter by backend name
 *   session_id  string   optional  filter by session
 *   limit       number   optional  max entries to return (default 20, max 200)
 *   status      string   optional  filter by "ok" | "error"
 */
app.get('/viewer', async (req, res) => {
  const { backend, session_id, status } = req.query;
  const limit = Math.min(parseInt(req.query.limit || '20', 10), 200);

  const filter = { source: 'kh-sim-log-service' };
  if (backend)    filter['context.backend']   = backend;
  if (session_id) filter['session_id']        = session_id;
  if (status)     filter['context.status']    = status;

  try {
    const docs = await collection()
      .find(filter)
      .sort({ '@timestamp': -1 })
      .limit(limit)
      .toArray();

    const entries = docs.map(d => ({
      id:              d._id,
      timestamp:       d['@timestamp'],
      backend:         d.context?.backend,
      session_id:      d.session_id,
      status:          d.context?.status,
      steps_completed: d.context?.steps_completed,
      t_final:         d.context?.t_final,
      compute_ms:      d.context?.compute_ms,
      diagnostics:     d.context?.diagnostics,
      params:          d.context?.params,
    }));

    return res.json({ entries, total: entries.length, limit, filter: { backend, session_id, status } });
  } catch (err) {
    logger.error('Viewer query failed', { err: err.message });
    return res.status(503).json({ error: 'Log storage unavailable', detail: err.message });
  }
});

// ── GET /summary ──────────────────────────────────────────────────────────────
/**
 * Per-backend aggregate stats.
 *
 * Returns for each known backend:
 *   count        total simulation events recorded
 *   ok_count     events with status="ok"
 *   error_count  events with status="error"
 *   avg_compute_ms
 *   last_seen    ISO timestamp of most recent event
 */
app.get('/summary', async (req, res) => {
  try {
    const pipeline = [
      { $match: { source: 'kh-sim-log-service' } },
      {
        $group: {
          _id:          '$context.backend',
          count:        { $sum: 1 },
          ok_count:     { $sum: { $cond: [{ $eq: ['$context.status', 'ok'] }, 1, 0] } },
          error_count:  { $sum: { $cond: [{ $eq: ['$context.status', 'error'] }, 1, 0] } },
          avg_ms:       { $avg: '$context.compute_ms' },
          last_seen:    { $max: '$@timestamp' },
        },
      },
      { $sort: { _id: 1 } },
    ];

    const rows = await collection().aggregate(pipeline).toArray();

    // Include all known backends even if no events yet
    const byBackend = Object.fromEntries(rows.map(r => [r._id, r]));
    const summary = [...VALID_BACKENDS].map(b => ({
      backend:        b,
      count:          byBackend[b]?.count        ?? 0,
      ok_count:       byBackend[b]?.ok_count     ?? 0,
      error_count:    byBackend[b]?.error_count  ?? 0,
      avg_compute_ms: byBackend[b]?.avg_ms != null
                        ? Math.round(byBackend[b].avg_ms * 10) / 10
                        : null,
      last_seen:      byBackend[b]?.last_seen    ?? null,
    }));

    return res.json({ summary, generated_at: new Date().toISOString() });
  } catch (err) {
    logger.error('Summary aggregation failed', { err: err.message });
    return res.status(503).json({ error: 'Log storage unavailable', detail: err.message });
  }
});

// ── GET /health ───────────────────────────────────────────────────────────────
app.get('/health', async (_req, res) => {
  let mongoStatus = 'disconnected';
  try {
    if (mongoClient) {
      await mongoClient.db('admin').command({ ping: 1 });
      mongoStatus = 'connected';
    }
  } catch {
    mongoStatus = 'error';
  }

  const healthy = mongoStatus === 'connected';
  return res.status(healthy ? 200 : 503).json({
    status:  healthy ? 'ok' : 'degraded',
    service: 'kh-sim-log-service',
    version: '1.0.0',
    port:    PORT,
    mongo:   mongoStatus,
    uptime_s: Math.round(process.uptime()),
  });
});

// ── GET /info ─────────────────────────────────────────────────────────────────
app.get('/info', (_req, res) => {
  res.json({
    service:       'kh-sim-log-service',
    version:       '1.0.0',
    description:   'KH-SIM simulation event recorder and per-backend viewer API',
    task:          'KH-014',
    port:          PORT,
    backends:      [...VALID_BACKENDS],
    routes: {
      'POST /event':   'Record a simulation event',
      'GET  /viewer':  'Query simulation log entries (?backend, ?limit, ?session_id, ?status)',
      'GET  /summary': 'Per-backend aggregate statistics',
      'GET  /health':  'Service and MongoDB health probe',
      'GET  /info':    'Service metadata',
    },
  });
});

// ── 404 ───────────────────────────────────────────────────────────────────────
app.use((_req, res) => res.status(404).json({ error: 'Not found' }));

// ── Startup ───────────────────────────────────────────────────────────────────
(async () => {
  await connectMongo();
  app.listen(PORT, '0.0.0.0', () => {
    logger.info(`kh-sim-log-service listening on :${PORT}`);
  });
})();
