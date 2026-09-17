"""Analytics and Spoilage Waste Prevention page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from freshness.constants import TYPE_DISPLAY_NAMES
from freshness.db.database import get_all_inventory_items, get_analytics_summary
from freshness.ui.styles import render_hero, render_section


def render_page() -> None:
    render_hero(
        eyebrow="FRESHGUARD VISION · ANALYTICS",
        title="Spoilage <em>prevention</em> & metrics.",
        latin_cycle=["Metrics & Trends", "Waste Reduction", "Inventory Health"],
        kicker="Analyze consumption trends, active inventory health, and spoilage prevention metrics.",
        specimen_no="ANALYTICS",
    )

    summary = get_analytics_summary()

    render_section("I.", "OVERVIEW", "Inventory health summary")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Scanned", summary["total_tracked"])
    with col2:
        st.metric("Active in Storage", summary["active_count"])
    with col3:
        st.metric("🟢 Fresh Items", summary["fresh_count"])
    with col4:
        st.metric("🟡 Use Soon", summary["use_soon_count"])
    with col5:
        st.metric("🔴 Expired", summary["expired_count"])

    render_section("II.", "PRODUCE DISTRIBUTION", "Item counts by produce type")

    dist = summary["produce_distribution"]
    if dist:
        df_dist = pd.DataFrame(
            [
                {
                    "Produce Type": TYPE_DISPLAY_NAMES.get(k, k.title()),
                    "Count": v,
                }
                for k, v in dist.items()
            ]
        ).sort_values(by="Count", ascending=False)

        col_left, col_right = st.columns([1.5, 1.0])
        with col_left:
            st.bar_chart(df_dist.set_index("Produce Type"))
        with col_right:
            st.dataframe(df_dist, hide_index=True, use_container_width=True)
    else:
        st.info("No produce items recorded yet in database.")

    render_section("III.", "DATA EXPORT", "Download inventory records")
    items = get_all_inventory_items()
    if items:
        export_data = [
            {
                "ID": item.id,
                "Produce": TYPE_DISPLAY_NAMES.get(item.produce_type, item.produce_type),
                "Condition": item.freshness_state,
                "Confidence": f"{item.confidence:.2f}",
                "Added Date": item.added_date,
                "Expiry Date": item.expiry_date,
                "Status": item.computed_status,
                "Source": item.source,
                "Tip": item.preservation_tip,
                "Notes": item.notes,
            }
            for item in items
        ]
        df_export = pd.DataFrame(export_data)
        csv_bytes = df_export.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Export Inventory Report to CSV",
            data=csv_bytes,
            file_name="freshguard_inventory_report.csv",
            mime="text/csv",
            use_container_width=True,
        )
