'''
Engineer: Taylor Roth
Date: 5/4/2022
Deliverable:
    Analyze RFGRNT of HRCH system trend points to correlate HRCH alarm status.
'''

import altair as alt
import pandas as pd
import streamlit as st

# Define the base time-series chart.
def get_chart(data):
    hover = alt.selection_single(
        fields=['date'],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data, title="BAS Parameters Over Time")
        .mark_line()
        .encode(
            x="Date",
            y="HRCH_1_CondPressure(psi)",
            color="symbol",
        )
    )

    # Draw points on the line, and highlight based on selection
    points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x="yearmonthdate(date)",
            y="BAS Parameter",
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip("date", title="Date"),
                alt.Tooltip("price", title="Price (USD)"),
            ],
        )
        .add_selection(hover)
    )
    return (lines + points + tooltips).interactive()

