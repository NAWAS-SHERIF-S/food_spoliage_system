"""Smart Refrigerator Inventory Manager page."""

from __future__ import annotations

import streamlit as st

from freshness.constants import (
    PRODUCE_LATIN,
    PRODUCE_TYPES,
    TYPE_DISPLAY_NAMES,
)
from freshness.db.database import (
    add_inventory_item,
    delete_inventory_item,
    get_all_inventory_items,
    update_item_status,
)
from freshness.services.shelflife import estimate_shelf_life, get_preservation_tip
from freshness.ui.styles import render_hero, render_section


def render_page() -> None:
    render_hero(
        eyebrow="FRESHGUARD VISION · SMART INVENTORY",
        title="Refrigerator <em>inventory</em> manager.",
        latin_cycle=[PRODUCE_LATIN[p] for p in PRODUCE_TYPES],
        kicker="Track food items, monitor expiration countdowns, and reduce spoilage waste.",
        specimen_no="INV-01",
    )

    render_section("I.", "MANUAL LOG", "Add item to inventory")
    with st.expander("➕ Add Produce Item Manually", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_type = st.selectbox(
                "Produce Type",
                options=PRODUCE_TYPES,
                format_func=lambda x: TYPE_DISPLAY_NAMES.get(x, x.title()),
            )
        with col2:
            selected_freshness = st.selectbox(
                "Freshness Condition",
                options=["fresh", "rotten"],
                format_func=lambda x: "Fresh" if x == "fresh" else "Rotten / Spoiled",
            )
        with col3:
            est = estimate_shelf_life(selected_type, selected_freshness, 1.0)
            custom_days = st.number_input(
                "Estimated Days Left",
                min_value=0,
                max_value=60,
                value=est.recommended_days,
            )

        notes = st.text_input("Notes (e.g. Crisper drawer, Batch A)")

        if st.button("Save Item to Inventory", use_container_width=True):
            tip = get_preservation_tip(selected_type)
            add_inventory_item(
                produce_type=selected_type,
                freshness_state=selected_freshness,
                confidence=1.0,
                estimated_days_left=int(custom_days),
                preservation_tip=tip,
                notes=notes,
                source="manual",
            )
            st.success(f"Added {TYPE_DISPLAY_NAMES[selected_type]} to inventory!")
            st.rerun()

    render_section("II.", "ACTIVE INVENTORY", "Current food items in storage")

    col_filter, col_search = st.columns([1, 2])
    with col_filter:
        status_filter = st.selectbox(
            "Filter Status",
            options=["All", "fresh", "use_soon", "expired", "consumed"],
            format_func=lambda x: {
                "All": "All Items",
                "fresh": "🟢 Fresh",
                "use_soon": "🟡 Use Soon",
                "expired": "🔴 Expired",
                "consumed": "⚪ Consumed",
            }.get(x, x),
        )

    db_filter = None if status_filter == "All" else status_filter
    items = get_all_inventory_items(status_filter=db_filter)

    if not items:
        st.info("No items found in inventory. Scan a produce specimen in the Lab or add one manually above!")
        return

    st.write(f"**Total Items**: {len(items)}")

    for item in items:
        status_badge = item.computed_status
        if status_badge == "fresh":
            badge_html = f'<span style="background: rgba(16, 185, 129, 0.2); color: #10b981; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.85rem;">🟢 FRESH ({item.days_remaining}d left)</span>'
        elif status_badge == "use_soon":
            badge_html = f'<span style="background: rgba(245, 158, 11, 0.2); color: #f59e0b; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.85rem;">🟡 USE SOON ({item.days_remaining}d left)</span>'
        elif status_badge == "expired":
            badge_html = '<span style="background: rgba(239, 68, 68, 0.2); color: #ef4444; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.85rem;">🔴 EXPIRED</span>'
        else:
            badge_html = '<span style="background: rgba(156, 163, 175, 0.2); color: #9ca3af; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.85rem;">⚪ CONSUMED</span>'

        display_name = TYPE_DISPLAY_NAMES.get(item.produce_type, item.produce_type.title())
        latin_name = PRODUCE_LATIN.get(item.produce_type, "")

        with st.container():
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                st.markdown(
                    f"### {display_name} <small style='color:#a0aec0;'>({latin_name})</small>",
                    unsafe_allow_html=True,
                )
                st.markdown(f"**Added**: `{item.added_date}` · **Expires**: `{item.expiry_date}`")
                if item.preservation_tip:
                    st.caption(f"💡 {item.preservation_tip}")
            with c2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(badge_html, unsafe_allow_html=True)
                if item.notes:
                    st.caption(f"Note: {item.notes}")
            with c3:
                st.markdown("<br>", unsafe_allow_html=True)
                if item.status != "consumed":
                    if st.button("Mark Consumed", key=f"con_{item.id}"):
                        update_item_status(item.id, "consumed")
                        st.toast("Marked as consumed!")
                        st.rerun()
                if st.button("Delete", key=f"del_{item.id}"):
                    delete_inventory_item(item.id)
                    st.toast("Item deleted")
                    st.rerun()
            st.divider()
