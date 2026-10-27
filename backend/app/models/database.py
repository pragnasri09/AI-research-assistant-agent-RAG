import sqlite3
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.config import settings

def get_db_connection():
    os.makedirs(os.path.dirname(settings.DB_PATH), exist_ok=True)
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS research_sessions (
        session_id TEXT PRIMARY KEY,
        question TEXT NOT NULL,
        status TEXT NOT NULL,
        progress_step TEXT NOT NULL,
        progress_percent INTEGER NOT NULL DEFAULT 0,
        sources_count INTEGER NOT NULL DEFAULT 0,
        report_json TEXT,
        report_markdown TEXT,
        error TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        source_number INTEGER NOT NULL,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        domain TEXT NOT NULL,
        publication_date TEXT,
        summary TEXT,
        key_findings_json TEXT,
        content TEXT,
        quality_score REAL DEFAULT 0.0,
        FOREIGN KEY (session_id) REFERENCES research_sessions (session_id) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    conn.close()

def save_session(session_id: str, question: str, status: str, progress_step: str, progress_percent: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    cursor.execute("""
    INSERT INTO research_sessions (session_id, question, status, progress_step, progress_percent, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(session_id) DO UPDATE SET
        status = excluded.status,
        progress_step = excluded.progress_step,
        progress_percent = excluded.progress_percent,
        updated_at = excluded.updated_at
    """, (session_id, question, status, progress_step, progress_percent, now, now))
    
    conn.commit()
    conn.close()

def update_session_report(session_id: str, status: str, progress_step: str, progress_percent: int, report_dict: Dict[str, Any], full_markdown: str, sources_count: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    cursor.execute("""
    UPDATE research_sessions
    SET status = ?,
        progress_step = ?,
        progress_percent = ?,
        sources_count = ?,
        report_json = ?,
        report_markdown = ?,
        updated_at = ?
    WHERE session_id = ?
    """, (status, progress_step, progress_percent, sources_count, json.dumps(report_dict), full_markdown, now, session_id))
    
    conn.commit()
    conn.close()

def update_session_error(session_id: str, error_message: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    cursor.execute("""
    UPDATE research_sessions
    SET status = 'failed',
        progress_step = 'Error encountered',
        error = ?,
        updated_at = ?
    WHERE session_id = ?
    """, (error_message, now, session_id))
    
    conn.commit()
    conn.close()

def save_sources(session_id: str, sources_list: List[Dict[str, Any]]):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clear previous sources if re-running
    cursor.execute("DELETE FROM sources WHERE session_id = ?", (session_id,))
    
    for idx, s in enumerate(sources_list, start=1):
        source_number = s.get("source_id", idx)
        key_findings = json.dumps(s.get("key_findings", []))
        
        cursor.execute("""
        INSERT INTO sources (session_id, source_number, title, url, domain, publication_date, summary, key_findings_json, content, quality_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            source_number,
            s.get("title", "Untitled Source"),
            s.get("url", ""),
            s.get("domain", ""),
            s.get("publication_date", "Unknown"),
            s.get("summary", ""),
            key_findings,
            s.get("content", ""),
            s.get("quality_score", 0.8)
        ))
    
    conn.commit()
    conn.close()

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM research_sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    res = dict(row)
    if res.get("report_json"):
        res["report"] = json.loads(res["report_json"])
    return res

def get_session_sources(session_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM sources WHERE session_id = ? ORDER BY source_number ASC", (session_id,))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        item = dict(r)
        item["source_id"] = item["source_number"]
        if item.get("key_findings_json"):
            item["key_findings"] = json.loads(item["key_findings_json"])
        else:
            item["key_findings"] = []
        results.append(item)
    return results

def get_history() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT session_id, question, status, sources_count, created_at, report_json
    FROM research_sessions
    ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for r in rows:
        item = dict(r)
        preview = ""
        if item.get("report_json"):
            try:
                rep = json.loads(item["report_json"])
                preview = rep.get("executive_summary", "")[:200] + "..." if rep.get("executive_summary") else ""
            except Exception:
                preview = ""
        history.append({
            "session_id": item["session_id"],
            "question": item["question"],
            "status": item["status"],
            "sources_count": item["sources_count"],
            "created_at": item["created_at"],
            "executive_summary_preview": preview
        })
    return history

def delete_session(session_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sources WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM research_sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
