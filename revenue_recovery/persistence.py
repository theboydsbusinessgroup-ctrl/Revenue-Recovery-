from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from .actions import ContactHistory
from .ledger import CanonicalOpportunity

class RecoveryStore:
    def __init__(self, path: str | Path = 'recovery_state.sqlite3'):
        self.path = str(path)
        self._init()

    def _connect(self):
        return sqlite3.connect(self.path)

    def _init(self):
        with self._connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS contact_history(
                quote_id TEXT PRIMARY KEY,
                attempts INTEGER NOT NULL DEFAULT 0,
                last_contact_days_ago INTEGER NOT NULL DEFAULT 999,
                negative_reply INTEGER NOT NULL DEFAULT 0
            )''')
            db.execute('''CREATE TABLE IF NOT EXISTS recovery_drafts(
                opportunity_id TEXT PRIMARY KEY,
                quote_id TEXT NOT NULL,
                provider TEXT NOT NULL,
                provider_draft_id TEXT,
                recipient TEXT NOT NULL,
                subject TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )''')
            db.execute('''CREATE TABLE IF NOT EXISTS canonical_opportunities(
                opportunity_id TEXT PRIMARY KEY,
                identity_key TEXT NOT NULL,
                recoverable INTEGER NOT NULL,
                recoverable_value REAL NOT NULL,
                currency TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )''')

    def get_history(self, quote_id: str) -> ContactHistory:
        with self._connect() as db:
            row = db.execute('SELECT attempts,last_contact_days_ago,negative_reply FROM contact_history WHERE quote_id=?',(quote_id,)).fetchone()
        if not row:
            return ContactHistory(quote_id)
        return ContactHistory(quote_id, int(row[0]), int(row[1]), bool(row[2]))

    def save_history(self, history: ContactHistory) -> None:
        with self._connect() as db:
            db.execute('''INSERT INTO contact_history(quote_id,attempts,last_contact_days_ago,negative_reply)
                VALUES(?,?,?,?) ON CONFLICT(quote_id) DO UPDATE SET attempts=excluded.attempts,last_contact_days_ago=excluded.last_contact_days_ago,negative_reply=excluded.negative_reply''',
                (history.quote_id,history.attempts,history.last_contact_days_ago,1 if history.negative_reply else 0))

    def record_draft(self, opportunity_id: str, quote_id: str, recipient: str, subject: str, provider_draft_id: str | None, status: str='drafted') -> None:
        with self._connect() as db:
            db.execute('''INSERT INTO recovery_drafts(opportunity_id,quote_id,provider,provider_draft_id,recipient,subject,status)
                VALUES(?,?,?,?,?,?,?) ON CONFLICT(opportunity_id) DO UPDATE SET provider_draft_id=excluded.provider_draft_id,status=excluded.status''',
                (opportunity_id,quote_id,'gmail',provider_draft_id,recipient,subject,status))

    def draft_for(self, opportunity_id: str):
        with self._connect() as db:
            row=db.execute('SELECT provider_draft_id,status FROM recovery_drafts WHERE opportunity_id=?',(opportunity_id,)).fetchone()
        return {'provider_draft_id':row[0],'status':row[1]} if row else None

    def save_canonical_opportunity(self, opportunity: CanonicalOpportunity) -> None:
        payload = json.dumps(opportunity.as_dict(), sort_keys=True)
        with self._connect() as db:
            db.execute('''INSERT INTO canonical_opportunities(opportunity_id,identity_key,recoverable,recoverable_value,currency,payload_json)
                VALUES(?,?,?,?,?,?) ON CONFLICT(opportunity_id) DO UPDATE SET identity_key=excluded.identity_key,recoverable=excluded.recoverable,recoverable_value=excluded.recoverable_value,currency=excluded.currency,payload_json=excluded.payload_json,updated_at=CURRENT_TIMESTAMP''',
                (opportunity.opportunity_id, opportunity.identity_key, 1 if opportunity.recoverable else 0, opportunity.recoverable_value_identified, opportunity.currency, payload))

    def load_canonical_opportunities(self) -> list[dict]:
        with self._connect() as db:
            rows = db.execute('SELECT payload_json FROM canonical_opportunities ORDER BY recoverable DESC,recoverable_value DESC').fetchall()
        return [json.loads(r[0]) for r in rows]
