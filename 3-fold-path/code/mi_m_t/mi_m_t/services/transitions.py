# =============================================================================
# mi_m_t/services/transitions.py — async TransitionService
# tags:    [μS-CAND][TRIG-REQ][CRIT-AUDIT]
# date:    2026-04-29
# citation: ARCH-SPEC §7.6 (canonical Python transition service),
#           §4.2 (seed), §4.3 ('any' expansion rule)
# =============================================================================
from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from mi_m_t.domain.statuses import ENTITY_TABLES, TransitionError, RoleError
from mi_m_t.config import settings

ANY_SENTINEL = "any"   # from_status sentinel per ARCH-SPEC §4.3


class TransitionService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def transition(
        self,
        entity_table: str,
        entity_id:    int,
        to_status:    str,
        user,
        note:         str | None = None,
    ):
        """
        Apply a lifecycle status transition inside a single transaction.

        Implements ARCH-SPEC §7.6 / mirrors PHP §6.5.1:
          1. SELECT current status (FOR UPDATE on MySQL/PG).
          2. Validate from→to pair in item_status_transitions (fans 'any').
          3. Role check: requires_role=NULL/'' → any role accepted.
          4. INSERT item_status_history row.
          5. UPDATE entity (item_status, date_of_adj_status, stat_adj_by_id, updated_at).

        Returns updated entity row as dict.
        Raises TransitionError (→ HTTP 409) or RoleError (→ HTTP 403).
        """
        if entity_table not in ENTITY_TABLES:
            raise TransitionError(f"invalid entity_table: '{entity_table}'")

        async with self.db.begin():
            # 1. Lock + read current status
            # SQLite does not support FOR UPDATE; MySQL/PG use row-level lock
            _lock = "" if settings.db_driver == "sqlite" else " FOR UPDATE"
            row = (await self.db.execute(
                text(f"SELECT item_status FROM {entity_table} WHERE id = :id{_lock}"),
                {"id": entity_id},
            )).first()

            if row is None:
                raise TransitionError(f"ENTITY_NOT_FOUND: {entity_table} id={entity_id}")

            from_status = row[0]
            if from_status == to_status:
                raise TransitionError(
                    f"NOOP_TRANSITION: {entity_table} id={entity_id} "
                    f"already in status '{to_status}'"
                )

            # 2. Allowed transitions — fans 'any' sentinel per §4.3
            rules = (await self.db.execute(
                text(
                    "SELECT requires_role FROM item_status_transitions"
                    " WHERE entity_table = :et"
                    "   AND (from_status = :from OR from_status = :any)"
                    "   AND to_status = :to"
                    "   AND is_active = true"  # OQ-034 (D-09): PG rejects integer literal for BOOLEAN
                ),
                {"et": entity_table, "from": from_status, "to": to_status, "any": ANY_SENTINEL},
            )).all()

            if not rules:
                raise TransitionError(
                    f"TRANSITION_NOT_ALLOWED: {entity_table} "
                    f"'{from_status}' -> '{to_status}' not in state machine"
                )

            # 3. Role check
            user_role = getattr(user, "role_in_process", None)
            if not any(r[0] in (None, "", user_role) for r in rules):
                required = [r[0] for r in rules if r[0]]
                raise RoleError(
                    f"ROLE_INSUFFICIENT: {entity_table} '{from_status}' -> '{to_status}' "
                    f"requires role in {required}, user has '{user_role}'"
                )

            now = datetime.now(timezone.utc).replace(tzinfo=None)

            # 4. Append-only audit history (ARCH-SPEC §1.5)
            await self.db.execute(
                text(
                    "INSERT INTO item_status_history"
                    " (entity_table, entity_id, from_status, to_status,"
                    "  changed_by_id, changed_at, note)"
                    " VALUES (:et, :eid, :from, :to, :uid, :ts, :note)"
                ),
                {
                    "et": entity_table, "eid": entity_id,
                    "from": from_status, "to": to_status,
                    "uid": user.id, "ts": now, "note": note,
                },
            )

            # 5. Update entity row
            await self.db.execute(
                text(
                    f"UPDATE {entity_table}"
                    " SET item_status = :to,"
                    "     date_of_adj_status = :ts,"
                    "     stat_adj_by_id = :uid,"
                    "     updated_at = :ts"
                    " WHERE id = :id"
                ),
                {"to": to_status, "ts": now, "uid": user.id, "id": entity_id},
            )

        # Re-read updated row outside the transaction
        result = (await self.db.execute(
            text(f"SELECT * FROM {entity_table} WHERE id = :id"), {"id": entity_id}
        )).mappings().first()
        return dict(result) if result else None
