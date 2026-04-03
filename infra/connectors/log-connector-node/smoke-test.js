/**
 * smoke-test.js  --  LOG-002 integration smoke test
 *
 * Verifies end-to-end log delivery from log-connector-node to:
 *   MongoDB  mongodb://127.0.0.1:27017/vibedev  collection: logs
 *   Elasticsearch  http://localhost:9200         index: kh-sim-YYYY.MM.DD
 *
 * Exit codes:
 *   0  all checks passed
 *   1  one or more checks failed
 *
 * Prerequisites:
 *   MongoDB 27017 running (DB-002 done)
 *   ELK stack up: .\_config\Start-LocalEnv.ps1 -Action up -Stack elk
 *   npm install (in this directory)
 *
 * Run:
 *   node smoke-test.js
 *   npm run smoke-test
 */

'use strict';

const { MongoClient } = require('mongodb');
const { Client: ESClient } = require('@elastic/elasticsearch');
const { createLogger } = require('./index');

const MONGO_URI = process.env.MONGODB_URI || 'mongodb://127.0.0.1:27017';
const ES_NODE   = process.env.ES_NODE     || 'http://localhost:9200';
const SESSION   = `smoke-${Date.now()}`;
const APP       = 'log-connector-smoke-test';

// ── Utilities ─────────────────────────────────────────────────────────────────

let passed = 0;
let failed = 0;

function ok(label)   { console.log(`  [PASS] ${label}`); passed++; }
function fail(label, detail) {
  console.error(`  [FAIL] ${label}${detail ? ': ' + detail : ''}`);
  failed++;
}

function header(text) {
  console.log(`\n${'─'.repeat(60)}`);
  console.log(`  ${text}`);
  console.log('─'.repeat(60));
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ── Main ─────────────────────────────────────────────────────────────────────

async function run() {
  header('LOG-002 smoke test — log-connector-node');

  // ── 1. Emit test events ───────────────────────────────────────────────────
  header('Step 1: emit structured log events');

  const logger = createLogger({
    app:       APP,
    sessionId: SESSION,
    version:   '1.0.0',
    level:     'debug',
    mongo:   { uri: MONGO_URI, db: 'vibedev', collection: 'logs' },
    elastic: { node: ES_NODE, indexPrefix: 'kh-sim' },
  });

  logger.info('Smoke test started', { step: 'init', session: SESSION });
  logger.debug('Debug event', { detail: 'low-level trace' });
  logger.warn('Intentional warning', { code: 'W001', threshold: 0.95 });
  logger.error('Intentional error (non-fatal)', { code: 'E001', recoverable: true });

  // Allow transports time to flush
  console.log('  Waiting 3s for transport flush...');
  await sleep(3000);

  // Explicitly close Mongo connection (Winston does not auto-close)
  for (const t of logger.transports) {
    if (typeof t.close === 'function') {
      await new Promise(res => t.close(res));
    }
  }

  ok('log events emitted (4 events: info, debug, warn, error)');

  // ── 2. Verify MongoDB ─────────────────────────────────────────────────────
  header('Step 2: verify MongoDB vibedev.logs');

  const mc = new MongoClient(MONGO_URI, { serverSelectionTimeoutMS: 5000 });
  try {
    await mc.connect();
    const col   = mc.db('vibedev').collection('logs');
    const count = await col.countDocuments({ session_id: SESSION, app: APP });

    if (count >= 4) {
      ok(`MongoDB: ${count} documents found for session ${SESSION}`);
    } else if (count > 0) {
      fail(`MongoDB: expected >= 4 docs, found ${count}`);
    } else {
      fail(`MongoDB: 0 documents found for session ${SESSION}`);
    }

    // Spot-check schema of one document
    const doc = await col.findOne({ session_id: SESSION, app: APP });
    if (doc) {
      const hasRequired = doc.level && doc.message && doc.app && doc.session_id &&
                          doc.metadata && doc.metadata.host && doc.metadata.pid;
      if (hasRequired) {
        ok('MongoDB: document schema valid (level, message, app, session_id, metadata.host, metadata.pid)');
      } else {
        fail('MongoDB: document missing required schema fields', JSON.stringify(doc));
      }
    }
  } catch (err) {
    fail('MongoDB: connection or query failed', err.message);
  } finally {
    await mc.close();
  }

  // ── 3. Verify Elasticsearch ───────────────────────────────────────────────
  header('Step 3: verify Elasticsearch kh-sim-* index');

  const es    = new ESClient({ node: ES_NODE, requestTimeout: 5000 });
  const today = new Date().toISOString().slice(0, 10).replace(/-/g, '.');
  const index = `kh-sim-${today}`;

  try {
    // Force index refresh so docs are visible to search immediately
    await es.indices.refresh({ index: `kh-sim-*` }).catch(() => {});

    // Diagnostic: total doc count in index (mapping-agnostic)
    const total = await es.count({ index: `kh-sim-*` });
    console.log(`  [INFO] Total docs in kh-sim-*: ${total.count}`);

    // ES 8 dynamic mapping: string fields → text + .keyword sub-field.
    // Use session_id.keyword for exact term match; fall back to match_phrase
    // against the analyzed text field if the index has no keyword sub-field.
    const result = await es.count({
      index:  `kh-sim-*`,
      query:  { term: { 'session_id.keyword': SESSION } },
    }).catch(() =>
      es.count({
        index: `kh-sim-*`,
        query: { match_phrase: { session_id: SESSION } },
      })
    );

    const count = result.count;
    if (count >= 4) {
      ok(`Elasticsearch: ${count} documents in ${index} for session ${SESSION}`);
    } else if (count > 0) {
      fail(`Elasticsearch: expected >= 4 docs, found ${count}`);
    } else {
      fail(`Elasticsearch: 0 documents found in ${index} for session ${SESSION}`);
    }

    // Spot-check mapping fields
    const hit = await es.search({
      index:  `kh-sim-*`,
      size:   1,
      query:  { term: { 'session_id.keyword': SESSION } },
    }).catch(() => null);

    if (hit && hit.hits.hits.length > 0) {
      const src = hit.hits.hits[0]._source;
      const hasTs = !!src['@timestamp'];
      const hasLvl = !!src.level;
      if (hasTs && hasLvl) {
        ok('Elasticsearch: document has @timestamp and level fields');
      } else {
        fail('Elasticsearch: document missing @timestamp or level', JSON.stringify(src));
      }
    }
  } catch (err) {
    fail('Elasticsearch: connection or query failed', err.message);
  }

  // ── 4. Cluster health sanity ──────────────────────────────────────────────
  header('Step 4: ES cluster health');
  try {
    const health = await es.cluster.health();
    if (health.status === 'green' || health.status === 'yellow') {
      ok(`Elasticsearch cluster: status=${health.status}, nodes=${health.number_of_nodes}`);
    } else {
      fail(`Elasticsearch cluster: unexpected status=${health.status}`);
    }
  } catch (err) {
    fail('Elasticsearch cluster health check failed', err.message);
  }

  // ── Summary ───────────────────────────────────────────────────────────────
  header('Summary');
  console.log(`  Passed: ${passed}`);
  console.log(`  Failed: ${failed}`);
  if (failed === 0) {
    console.log('\n  LOG-002 smoke test PASSED -- log-connector-node operational\n');
    process.exit(0);
  } else {
    console.error('\n  LOG-002 smoke test FAILED -- see [FAIL] lines above\n');
    process.exit(1);
  }
}

run().catch(err => {
  console.error('[smoke-test] Unhandled error:', err);
  process.exit(1);
});
