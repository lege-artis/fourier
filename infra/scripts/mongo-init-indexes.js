/**
 * mongo-init-indexes.js  --  VibeCodeProjects MongoDB index initialisation
 * Project: KH-Sim / infra  |  Task: LOG-006
 *
 * Creates all operational indexes on vibedev.logs.
 * Safe to re-run: MongoDB createIndex() is idempotent -- existing indexes with
 * identical key + options are left untouched; only missing ones are created.
 *
 * Run:
 *   mongosh mongodb://127.0.0.1:27017/vibedev infra/scripts/mongo-init-indexes.js
 *
 * Or from mongosh interactive shell:
 *   load("infra/scripts/mongo-init-indexes.js")
 *
 * Architecture reference: infra/LOG-ARCHITECTURE.md
 */

// ── Configuration ──────────────────────────────────────────────────────────────

const DB_NAME         = "vibedev";
const COLLECTION_NAME = "logs";
const TTL_DAYS        = 30;
const TTL_SECONDS     = TTL_DAYS * 24 * 60 * 60;   // 2592000

// ── Helpers ────────────────────────────────────────────────────────────────────

function ensureIndex(col, keyPattern, options, label) {
  try {
    const result = col.createIndex(keyPattern, options);
    if (result === label || typeof result === "string") {
      print(`  [OK]      ${label}  (created)`);
    } else {
      print(`  [OK]      ${label}  (already exists)`);
    }
  } catch (e) {
    print(`  [ERROR]   ${label}: ${e.message}`);
    throw e;
  }
}

// ── Main ───────────────────────────────────────────────────────────────────────

print("─────────────────────────────────────────────────────────");
print("  mongo-init-indexes.js  --  vibedev.logs");
print("─────────────────────────────────────────────────────────");

const db  = db.getSiblingDB(DB_NAME);
const col = db.getCollection(COLLECTION_NAME);

// Confirm collection is reachable
const docCount = col.countDocuments({});
print(`\n  Collection: ${DB_NAME}.${COLLECTION_NAME}  (${docCount} documents)\n`);

// ── Query indexes ──────────────────────────────────────────────────────────────

print("  Query indexes:");

ensureIndex(
  col,
  { timestamp: -1 },
  { name: "timestamp_desc" },
  "timestamp_desc"
);

ensureIndex(
  col,
  { level: 1, timestamp: -1 },
  { name: "level_timestamp" },
  "level_timestamp"
);

ensureIndex(
  col,
  { app: 1, timestamp: -1 },
  { name: "app_timestamp" },
  "app_timestamp"
);

ensureIndex(
  col,
  { session_id: 1 },
  { name: "session_id" },
  "session_id"
);

// ── TTL index ──────────────────────────────────────────────────────────────────

print("\n  TTL index (retention):");

ensureIndex(
  col,
  { timestamp: 1 },
  { name: "ttl_30d", expireAfterSeconds: TTL_SECONDS },
  "ttl_30d"
);

// ── Verification ───────────────────────────────────────────────────────────────

print("\n  Index summary:");
const indexes = col.getIndexes();
indexes.forEach(idx => {
  const ttlNote = idx.expireAfterSeconds !== undefined
    ? `  [TTL: ${idx.expireAfterSeconds / 86400}d]`
    : "";
  print(`    ${idx.name.padEnd(25)} key: ${JSON.stringify(idx.key)}${ttlNote}`);
});

print(`\n  Total indexes: ${indexes.length}`);
print("  Done.\n");
