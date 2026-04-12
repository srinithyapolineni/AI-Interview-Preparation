"""
database.py
SQLite-based persistence layer for user interview history and performance stats.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "interview_data.db")


class DatabaseManager:
    def __init__(self):
        self._init_db()

    # ── Setup ──────────────────────────────────────────────────────────────

    def _init_db(self):
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    username  TEXT    NOT NULL,
                    role      TEXT    NOT NULL,
                    question  TEXT    NOT NULL,
                    answer    TEXT    NOT NULL,
                    score     INTEGER NOT NULL,
                    timestamp TEXT    NOT NULL
                )
            """)

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(DB_PATH)

    # ── Write ──────────────────────────────────────────────────────────────

    def save_result(self, username: str, question: str, answer: str,
                    score: int, role: str):
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO results
                   (username, role, question, answer, score, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (username, role, question, answer, score,
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )

    def reset(self, username: str):
        with self._conn() as conn:
            conn.execute("DELETE FROM results WHERE username = ?", (username,))

    # ── Read ───────────────────────────────────────────────────────────────

    def get_stats(self, username: str) -> dict:
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT role, score, timestamp
                   FROM results WHERE username = ?
                   ORDER BY timestamp DESC""",
                (username,)
            ).fetchall()

        if not rows:
            return {
                "username":       username,
                "total_sessions": 0,
                "average_score":  0,
                "best_score":     0,
                "history":        [],
                "role_breakdown": {},
            }

        scores     = [r[1] for r in rows]
        role_scores: dict = {}
        for role, score, _ in rows:
            role_scores.setdefault(role, []).append(score)

        role_breakdown = {
            role: round(sum(s) / len(s), 1)
            for role, s in role_scores.items()
        }

        history = [
            {"role": r[0], "score": r[1], "timestamp": r[2]}
            for r in rows[:20]  # last 20
        ]

        return {
            "username":       username,
            "total_sessions": len(rows),
            "average_score":  round(sum(scores) / len(scores), 1),
            "best_score":     max(scores),
            "history":        history,
            "role_breakdown": role_breakdown,
        }

    def get_recent(self, username: str, limit: int = 5) -> list:
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT question, answer, score, role, timestamp
                   FROM results WHERE username = ?
                   ORDER BY timestamp DESC LIMIT ?""",
                (username, limit)
            ).fetchall()
        return [
            {"question": r[0], "answer": r[1], "score": r[2],
             "role": r[3], "timestamp": r[4]}
            for r in rows
        ]
