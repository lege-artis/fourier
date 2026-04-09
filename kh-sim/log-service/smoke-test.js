/**
 * smoke-test.js  --  kh-sim-log-service connectivity smoke test
 * Task: KH-014
 *
 * Usage:
 *   node smoke-test.js                      # target http://localhost:8006
 *   KH_LOG_URL=http://kh-log.test:8080 node smoke-test.js
 *
 * Exit 0 = all checks pass, Exit 1 = any failure
 */

'use strict';

const http    = require('http');
const baseUrl = process.env.KH_LOG_URL || 'http://localhost:8006';

let passed = 0;
let failed = 0;

function req(method, path, body) {
  return new Promise((resolve, reject) => {
    const url  = new URL(path, baseUrl);
    const data = body ? JSON.stringify(body) : null;
    const opts = {
      hostname: url.hostname,
      port:     url.port || 80,
      path:     url.pathname + url.search,
      method,
      headers:  {
        'Content-Type':   'application/json',
        'Content-Length': data ? Buffer.byteLength(data) : 0,
      },
    };
    const r = http.request(opts, (res) => {
      let raw = '';
      res.on('data', c => raw += c);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(raw) }); }
        catch { resolve({ status: res.statusCode, body: raw }); }
      });
    });
    r.on('error', reject);
    if (data) r.write(data);
    r.end();
  });
}

function ok(label, cond, detail) {
  if (cond) {
    console.log(`  [PASS]  ${label}`);
    passed++;
  } else {
    console.log(`  [FAIL]  ${label}${detail ? ' -- ' + detail : ''}`);
    failed++;
  }
}

async function run() {
  console.log(`\nkh-sim-log-service smoke test  ->  ${baseUrl}\n`);

  // ── 1. /health ────────────────────────────────────────────────────────────
  console.log('1. Health check');
  try {
    const r = await req('GET', '/health');
    ok('/health responds 200 or 503',    [200,503].includes(r.status), `got ${r.status}`);
    ok('/health body has status field',  r.body && 'status' in r.body);
    ok('/health body has mongo field',   r.body && 'mongo'  in r.body);
  } catch (e) {
    ok('/health reachable', false, e.message);
  }

  // ── 2. /info ──────────────────────────────────────────────────────────────
  console.log('\n2. Service info');
  try {
    const r = await req('GET', '/info');
    ok('/info responds 200',             r.status === 200,          `got ${r.status}`);
    ok('/info has backends array',       Array.isArray(r.body?.backends));
    ok('/info has routes object',        r.body?.routes && typeof r.body.routes === 'object');
  } catch (e) {
    ok('/info reachable', false, e.message);
  }

  // ── 3. POST /event -- valid ───────────────────────────────────────────────
  console.log('\n3. POST /event (valid payload)');
  let eventId;
  try {
    const payload = {
      backend:         'kh-rust',
      session_id:      'smoke-test-session',
      steps_completed: 50,
      t_final:         0.05,
      compute_ms:      120.5,
      params:          { grid_nx: 64, grid_ny: 32, dt: 0.001, steps: 50 },
      diagnostics:     { kinetic_energy: 0.42, enstrophy: 1.1, max_vorticity: 3.2 },
      status:          'ok',
    };
    const r = await req('POST', '/event', payload);
    ok('POST /event responds 201',       r.status === 201,          `got ${r.status}`);
    ok('response has id field',          r.body && 'id' in r.body);
    ok('response status is recorded',    r.body?.status === 'recorded');
    eventId = r.body?.id;
  } catch (e) {
    ok('POST /event reachable', false, e.message);
  }

  // ── 4. POST /event -- invalid backend ─────────────────────────────────────
  console.log('\n4. POST /event (invalid backend)');
  try {
    const r = await req('POST', '/event', { backend: 'kh-unknown' });
    ok('POST /event with bad backend = 400', r.status === 400, `got ${r.status}`);
    ok('response has error field',           r.body && 'error' in r.body);
  } catch (e) {
    ok('POST /event validation reachable', false, e.message);
  }

  // ── 5. GET /viewer ────────────────────────────────────────────────────────
  console.log('\n5. GET /viewer');
  try {
    const r = await req('GET', '/viewer?backend=kh-rust&limit=5');
    ok('/viewer responds 200 or 503',    [200,503].includes(r.status), `got ${r.status}`);
    if (r.status === 200) {
      ok('/viewer has entries array',    Array.isArray(r.body?.entries));
      ok('/viewer respects limit param', (r.body?.entries?.length ?? 0) <= 5);
    }
  } catch (e) {
    ok('/viewer reachable', false, e.message);
  }

  // ── 6. GET /summary ───────────────────────────────────────────────────────
  console.log('\n6. GET /summary');
  try {
    const r = await req('GET', '/summary');
    ok('/summary responds 200 or 503',   [200,503].includes(r.status), `got ${r.status}`);
    if (r.status === 200) {
      ok('/summary has summary array',   Array.isArray(r.body?.summary));
      ok('/summary covers all backends', r.body?.summary?.length === 5);
    }
  } catch (e) {
    ok('/summary reachable', false, e.message);
  }

  // ── Result ────────────────────────────────────────────────────────────────
  const total = passed + failed;
  console.log(`\n${'─'.repeat(50)}`);
  console.log(`Result: ${passed}/${total} checks passed${failed ? ' -- ' + failed + ' FAILED' : ''}`);
  console.log('');
  process.exit(failed > 0 ? 1 : 0);
}

run().catch(e => { console.error('Smoke test error:', e.message); process.exit(1); });
