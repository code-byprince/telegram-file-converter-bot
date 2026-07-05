import sqlite3
import os
import threading
from datetime import datetime

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "stats.db"
)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

_lock = threading.Lock()


def _get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    """Bot start hote hi tables bana deta hai (agar pehle se nahi hain)."""
    with _lock:
        conn = _get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                first_seen TEXT,
                language TEXT DEFAULT 'hi'
            )
        """)
        # Purani DB me agar language column nahi hai, toh add kar do (safe migration)
        try:
            conn.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'hi'")
            conn.commit()
        except sqlite3.OperationalError:
            pass  # column already exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feature_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                feature TEXT,
                used_at TEXT
            )
        """)
        conn.commit()
        conn.close()


def log_user(user_id: int, username: str, first_name: str):
    """Naya user /start karega toh usko record kar leta hai (purana ho toh ignore)."""
    with _lock:
        conn = _get_conn()
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name, first_seen) VALUES (?, ?, ?, ?)",
            (user_id, username or "", first_name or "", datetime.utcnow().isoformat()),
        )
        conn.commit()
        conn.close()


def log_feature_use(user_id: int, feature: str):
    """Har successful conversion pe ek entry daal deta hai."""
    with _lock:
        conn = _get_conn()
        conn.execute(
            "INSERT INTO feature_usage (user_id, feature, used_at) VALUES (?, ?, ?)",
            (user_id, feature, datetime.utcnow().isoformat()),
        )
        conn.commit()
        conn.close()


def get_language(user_id: int) -> str:
    """User ki saved language return karta hai, default 'hi' (Hinglish)."""
    with _lock:
        conn = _get_conn()
        row = conn.execute("SELECT language FROM users WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
    return row[0] if row and row[0] else "hi"


def set_language(user_id: int, lang: str):
    """User ki language preference save karta hai ('hi' ya 'en')."""
    with _lock:
        conn = _get_conn()
        conn.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))
        conn.commit()
        conn.close()


def get_history(user_id: int, limit: int = 5) -> list:
    """User ki last N conversions return karta hai (feature, used_at)."""
    with _lock:
        conn = _get_conn()
        rows = conn.execute(
            "SELECT feature, used_at FROM feature_usage WHERE user_id = ? ORDER BY used_at DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        conn.close()
    return rows


def get_stats() -> dict:
    """Admin /stats command ke liye summary nikalta hai."""
    with _lock:
        conn = _get_conn()
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_conversions = conn.execute("SELECT COUNT(*) FROM feature_usage").fetchone()[0]
        active_today = conn.execute(
            "SELECT COUNT(DISTINCT user_id) FROM feature_usage WHERE used_at >= date('now')"
        ).fetchone()[0]
        feature_breakdown = conn.execute(
            "SELECT feature, COUNT(*) as cnt FROM feature_usage GROUP BY feature ORDER BY cnt DESC"
        ).fetchall()
        conn.close()
    return {
        "total_users": total_users,
        "total_conversions": total_conversions,
        "active_today": active_today,
        "feature_breakdown": feature_breakdown,
    }
    
