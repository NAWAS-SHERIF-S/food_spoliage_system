"""SQLite database manager for FreshGuard inventory and scan history persistence."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from freshness.config import ROOT_DIR

DB_PATH = ROOT_DIR / "freshness.db"


@dataclass(slots=True)
class InventoryItem:
    id: int
    produce_type: str
    freshness_state: str
    confidence: float
    estimated_days_left: int
    added_date: str
    expiry_date: str
    status: str  # "fresh", "use_soon", "expired", "consumed"
    preservation_tip: str
    notes: str = ""
    source: str = "scan"

    @property
    def days_remaining(self) -> int:
        """Calculate real-time days remaining until expiry_date."""
        try:
            exp = datetime.strptime(self.expiry_date, "%Y-%m-%d").date()
            today = date.today()
            return (exp - today).days
        except ValueError:
            return self.estimated_days_left

    @property
    def computed_status(self) -> str:
        """Return status badge based on remaining days."""
        if self.status == "consumed":
            return "consumed"
        rem = self.days_remaining
        if rem <= 0:
            return "expired"
        elif rem <= 2:
            return "use_soon"
        return "fresh"


from contextlib import contextmanager

@contextmanager
def _get_connection(db_file: Path | str = DB_PATH):
    conn = sqlite3.connect(str(db_file), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()



def init_db(db_file: Path | str = DB_PATH) -> None:
    """Initialize database schema if tables do not exist."""
    with _get_connection(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produce_type TEXT NOT NULL,
                freshness_state TEXT NOT NULL,
                confidence REAL NOT NULL,
                estimated_days_left INTEGER NOT NULL,
                added_date TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'fresh',
                preservation_tip TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                source TEXT DEFAULT 'scan'
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_name TEXT,
                num_detections INTEGER,
                timestamp TEXT NOT NULL
            )
            """
        )
        conn.commit()


def add_inventory_item(
    produce_type: str,
    freshness_state: str,
    confidence: float,
    estimated_days_left: int,
    preservation_tip: str = "",
    notes: str = "",
    source: str = "scan",
    db_file: Path | str = DB_PATH,
) -> int:
    """Add a new item into the inventory database."""
    init_db(db_file)
    today = date.today()
    exp_date = today + timedelta(days=max(0, estimated_days_left))
    
    status = "fresh"
    if estimated_days_left <= 0:
        status = "expired"
    elif estimated_days_left <= 2:
        status = "use_soon"

    with _get_connection(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO inventory (
                produce_type, freshness_state, confidence, estimated_days_left,
                added_date, expiry_date, status, preservation_tip, notes, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                produce_type,
                freshness_state,
                confidence,
                estimated_days_left,
                today.isoformat(),
                exp_date.isoformat(),
                status,
                preservation_tip,
                notes,
                source,
            ),
        )
        conn.commit()
        return cursor.lastrowid or 0


def get_all_inventory_items(
    db_file: Path | str = DB_PATH, status_filter: str | None = None
) -> list[InventoryItem]:
    """Retrieve all inventory items, optionally filtered by status."""
    init_db(db_file)
    query = "SELECT * FROM inventory ORDER BY expiry_date ASC"
    params: tuple[Any, ...] = ()
    if status_filter:
        query = "SELECT * FROM inventory WHERE status = ? ORDER BY expiry_date ASC"
        params = (status_filter,)

    with _get_connection(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

    items: list[InventoryItem] = []
    for row in rows:
        items.append(
            InventoryItem(
                id=row["id"],
                produce_type=row["produce_type"],
                freshness_state=row["freshness_state"],
                confidence=row["confidence"],
                estimated_days_left=row["estimated_days_left"],
                added_date=row["added_date"],
                expiry_date=row["expiry_date"],
                status=row["status"],
                preservation_tip=row["preservation_tip"] or "",
                notes=row["notes"] or "",
                source=row["source"] or "scan",
            )
        )
    return items


def update_item_status(item_id: int, new_status: str, db_file: Path | str = DB_PATH) -> None:
    """Update item status (e.g., mark as 'consumed' or 'expired')."""
    init_db(db_file)
    with _get_connection(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE inventory SET status = ? WHERE id = ?", (new_status, item_id))
        conn.commit()


def delete_inventory_item(item_id: int, db_file: Path | str = DB_PATH) -> None:
    """Delete an item from inventory."""
    init_db(db_file)
    with _get_connection(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        conn.commit()


def log_scan_event(
    image_name: str, num_detections: int, db_file: Path | str = DB_PATH
) -> None:
    """Log an image scan event in history."""
    init_db(db_file)
    with _get_connection(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO scan_history (image_name, num_detections, timestamp) VALUES (?, ?, ?)",
            (image_name, num_detections, datetime.now().isoformat()),
        )
        conn.commit()


def get_analytics_summary(db_file: Path | str = DB_PATH) -> dict[str, Any]:
    """Calculate summary statistics for inventory analytics dashboard."""
    items = get_all_inventory_items(db_file)
    total_items = len(items)
    active_items = [item for item in items if item.status != "consumed"]
    fresh_count = sum(1 for item in active_items if item.computed_status == "fresh")
    use_soon_count = sum(1 for item in active_items if item.computed_status == "use_soon")
    expired_count = sum(1 for item in active_items if item.computed_status == "expired")
    consumed_count = sum(1 for item in items if item.status == "consumed")

    produce_counts: dict[str, int] = {}
    for item in items:
        ptype = item.produce_type
        produce_counts[ptype] = produce_counts.get(ptype, 0) + 1

    return {
        "total_tracked": total_items,
        "active_count": len(active_items),
        "fresh_count": fresh_count,
        "use_soon_count": use_soon_count,
        "expired_count": expired_count,
        "consumed_count": consumed_count,
        "produce_distribution": produce_counts,
    }
