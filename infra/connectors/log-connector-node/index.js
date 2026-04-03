/**
 * log-connector-node  --  VibeCodeProjects structured log connector
 * Project: KH-Sim / infra  |  Task: LOG-002
 *
 * Dual-sink Winston logger:
 *   MongoDB  vibedev.logs  -- app runtime events (flexible schema, 30-day TTL)
 *   Elasticsearch  {prefix}-YYYY.MM.DD  -- CI/test/structured diagnostics
 *
 * Both sinks are optional; omit a config key to disable that sink.
 *
 * Schema: infra/connectors/LOG-CONNECTOR-SPEC.md
 * Architecture: infra/LOG-ARCHITECTURE.md
 *
 * Usage:
 *   const { createLogger } = require('./index');
 *   const logger = createLogger({
 *     app: 'kh-rust',
 *     sessionId: process.env.SESSION_ID,
 *     mongo:   { uri: 'mongodb://127.0.0.1:27017', db: 'vibedev', collection: 'logs' },
 *     elastic: { node: 'http://localhost:9200', indexPrefix: 'kh-sim' },
 *   });
 *   logger.info('Simulation started', { params: { kx: 1.0, ky: 0.5 } });
 */

'use strict';

const os      = require('os');
const winston = require('winston');
const { MongoClient } = require('mongodb');
const { Client: ESClient } = require('@elastic/elasticsearch');

// ── Helpers ──────────────────────────────────────────────────────────────────

function utcDateStr() {
  return new Date().toISOString().slice(0, 10).replace(/-/g, '.');
}

function buildDoc(info, defaultMeta) {
  const { level, message, ...rest } = info;
  return {
    '@timestamp': new Date().toISOString(),
    level,
    message,
    source:     defaultMeta.source     || defaultMeta.app || 'unknown',
    app:        defaultMeta.app        || 'unknown',
    session_id: defaultMeta.session_id || 'none',
    metadata: {
      host:    os.hostname(),
      pid:     process.pid,
      env:     process.env.NODE_ENV || 'development',
      version: defaultMeta.version   || '0.0.0',
    },
    context: rest,
  };
}

// ── MongoDB transport ─────────────────────────────────────────────────────────

class MongoTransport extends winston.Transport {
  /**
   * @param {object} opts
   * @param {string}  opts.uri        MongoDB connection string
   * @param {string}  [opts.db]       Database name (default: 'vibedev')
   * @param {string}  [opts.collection]  Collection name (default: 'logs')
   * @param {object}  [opts.defaultMeta] Merged into every document
   */
  constructor(opts) {
    super(opts);
    this.name        = 'MongoTransport';
    this.db          = opts.db         || 'vibedev';
    this.collection  = opts.collection || 'logs';
    this.defaultMeta = opts.defaultMeta || {};
    this._ready      = false;
    this._queue      = [];

    this._client = new MongoClient(opts.uri, { serverSelectionTimeoutMS: 5000 });
    this._client.connect()
      .then(() => {
        this._col   = this._client.db(this.db).collection(this.collection);
        this._ready = true;
        // Drain buffered events
        const buffered = this._queue.splice(0);
        for (const { doc, cb } of buffered) {
          this._insert(doc, cb);
        }
      })
      .catch(err => {
        process.stderr.write(`[MongoTransport] connect failed: ${err.message}\n`);
        // Discard buffered events gracefully -- do not crash the process
        this._queue.splice(0).forEach(({ cb }) => cb());
      });
  }

  _insert(doc, callback) {
    this._col.insertOne(doc)
      .then(() => callback())
      .catch(err => {
        process.stderr.write(`[MongoTransport] insert error: ${err.message}\n`);
        callback(); // swallow -- logging must not crash the host process
      });
  }

  log(info, callback) {
    setImmediate(() => this.emit('logged', info));
    const doc = buildDoc(info, this.defaultMeta);
    // Re-stamp timestamp as native Date for MongoDB TTL index compatibility
    doc.timestamp = new Date(doc['@timestamp']);
    if (this._ready) {
      this._insert(doc, callback);
    } else {
      this._queue.push({ doc, cb: callback });
    }
  }

  close(callback) {
    this._client.close().then(() => callback && callback()).catch(() => callback && callback());
  }
}

// ── Elasticsearch transport ───────────────────────────────────────────────────

class ESTransport extends winston.Transport {
  /**
   * @param {object} opts
   * @param {string}  opts.node         Elasticsearch base URL
   * @param {string}  [opts.indexPrefix] Index prefix (default: 'app-logs')
   *                                    Final index: {prefix}-YYYY.MM.DD
   * @param {object}  [opts.defaultMeta] Merged into every document
   */
  constructor(opts) {
    super(opts);
    this.name        = 'ESTransport';
    this.indexPrefix = opts.indexPrefix || 'app-logs';
    this.defaultMeta = opts.defaultMeta || {};
    this._es         = new ESClient({ node: opts.node, requestTimeout: 5000 });
  }

  log(info, callback) {
    setImmediate(() => this.emit('logged', info));
    const doc   = buildDoc(info, this.defaultMeta);
    const index = `${this.indexPrefix}-${utcDateStr()}`;
    this._es.index({ index, document: doc })
      .then(() => callback())
      .catch(err => {
        process.stderr.write(`[ESTransport] index error (${index}): ${err.message}\n`);
        callback();
      });
  }
}

// ── Factory ───────────────────────────────────────────────────────────────────

/**
 * createLogger — build a Winston logger with optional MongoDB + ES sinks.
 *
 * @param {object}  config
 * @param {string}  config.app           Application / service name (required)
 * @param {string}  [config.sessionId]   Dev/test session UUID
 * @param {string}  [config.version]     App version string
 * @param {string}  [config.level]       Minimum log level (default: process.env.LOG_LEVEL || 'info')
 * @param {object}  [config.mongo]       MongoDB sink config (omit to disable)
 * @param {string}   config.mongo.uri
 * @param {string}   [config.mongo.db]
 * @param {string}   [config.mongo.collection]
 * @param {object}  [config.elastic]     Elasticsearch sink config (omit to disable)
 * @param {string}   config.elastic.node
 * @param {string}   [config.elastic.indexPrefix]
 * @returns {winston.Logger}
 */
function createLogger(config) {
  if (!config || !config.app) {
    throw new Error('log-connector-node: config.app is required');
  }

  const defaultMeta = {
    app:        config.app,
    source:     config.app,
    session_id: config.sessionId || process.env.LOG_SESSION_ID || 'none',
    version:    config.version   || process.env.npm_package_version || '0.0.0',
  };

  const level      = config.level || process.env.LOG_LEVEL || 'info';
  const transports = [];

  // Always include console (stderr-friendly, non-colorized in CI)
  transports.push(new winston.transports.Console({
    level,
    format: winston.format.combine(
      winston.format.timestamp(),
      winston.format.printf(({ timestamp, level: lvl, message, ...meta }) => {
        const ctx = Object.keys(meta).length ? ` ${JSON.stringify(meta)}` : '';
        return `${timestamp} [${config.app}] ${lvl.toUpperCase()}: ${message}${ctx}`;
      })
    ),
  }));

  // MongoDB sink
  if (config.mongo && config.mongo.uri) {
    transports.push(new MongoTransport({
      level,
      uri:         config.mongo.uri,
      db:          config.mongo.db         || 'vibedev',
      collection:  config.mongo.collection || 'logs',
      defaultMeta,
    }));
  }

  // Elasticsearch sink
  if (config.elastic && config.elastic.node) {
    transports.push(new ESTransport({
      level,
      node:        config.elastic.node,
      indexPrefix: config.elastic.indexPrefix || 'app-logs',
      defaultMeta,
    }));
  }

  return winston.createLogger({
    level,
    defaultMeta,
    transports,
    exitOnError: false,
  });
}

module.exports = { createLogger, MongoTransport, ESTransport };
