"""Unit tests for database and shelf-life services extension."""

from __future__ import annotations

import os
from pathlib import Path

from freshness.db.database import (
    add_inventory_item,
    delete_inventory_item,
    get_all_inventory_items,
    get_analytics_summary,
    init_db,
    update_item_status,
)
from freshness.services.shelflife import estimate_shelf_life, get_preservation_tip

TEST_DB = Path("test_freshness.db")


def test_shelf_life_estimation() -> None:
    # Test fresh apple
    est_apple = estimate_shelf_life("apple", "fresh", 0.95)
    assert est_apple.days_min > 0
    assert "Fresh" in est_apple.status_badge
    assert len(est_apple.preservation_tip) > 5

    # Test rotten banana
    est_rotten = estimate_shelf_life("banana", "rotten", 0.99)
    assert est_rotten.recommended_days == 0
    assert "Spoiled" in est_rotten.status_badge

    print("[PASS] Shelf-life estimation tests passed!")


def test_database_crud() -> None:
    if TEST_DB.exists():
        os.remove(TEST_DB)

    init_db(TEST_DB)

    item_id = add_inventory_item(
        produce_type="tomato",
        freshness_state="fresh",
        confidence=0.92,
        estimated_days_left=7,
        preservation_tip="Keep stem-side down.",
        notes="Batch 1",
        source="scan",
        db_file=TEST_DB,
    )
    assert item_id > 0

    items = get_all_inventory_items(TEST_DB)
    assert len(items) == 1
    assert items[0].produce_type == "tomato"
    assert items[0].days_remaining <= 7

    update_item_status(item_id, "consumed", TEST_DB)
    items_after = get_all_inventory_items(TEST_DB)
    assert items_after[0].status == "consumed"

    summary = get_analytics_summary(TEST_DB)
    assert summary["total_tracked"] == 1
    assert summary["consumed_count"] == 1

    delete_inventory_item(item_id, TEST_DB)
    assert len(get_all_inventory_items(TEST_DB)) == 0

    if TEST_DB.exists():
        os.remove(TEST_DB)

    print("[PASS] Database CRUD tests passed!")


if __name__ == "__main__":
    test_shelf_life_estimation()
    test_database_crud()
