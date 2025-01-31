import streamlit as st
import requests
import time
import math
import pandas as pd
import os

# Title
st.title("Polished Stone Value (PSV) Calculator Results")

# Input parameters
st.sidebar.title("Polished Stone Value (PSV) Calculator")
st.sidebar.header("Enter values:")

# Create a session state to store multiple entries
if 'entries' not in st.session_state:
    st.session_state.entries = []

def add_entry():
    st.session_state.entries.append({
        'aadt_value': 0,
        'per_hgvs': 0,
        'year': 0,
        'lanes': 1
    })

# Button to add new entries
st.sidebar.button("Add Entry", on_click=add_entry)

# Iterate over the entries for dynamic input
for idx, entry in enumerate(st.session_state.entries):
    with st.sidebar.expander(f"Entry {idx+1}"):
        entry['aadt_value'] = st.number_input(f"Enter AADT value for Entry {idx+1}:", min_value=0, key=f"aadt_{idx}")
        entry['per_hgvs'] = st.number_input(f"Enter % of HGVs for Entry {idx+1}:", key=f"per_hgvs_{idx}")
        entry['year'] = st.number_input(f"Enter Year for Entry {idx+1}:", min_value=0, key=f"year_{idx}")
        entry['lanes'] = st.number_input(f"Enter number of lanes for Entry {idx+1}:", min_value=1, key=f"lanes_{idx}")

# Link section
st.sidebar.header("Links Section")
st.sidebar.text("Here you can add links related to PSV or your project.")
st.sidebar.text_input("Enter a link title:")
link_url = st.sidebar.text_input("Enter the link URL:")

if link_url:
    st.sidebar.markdown(f"[{link_url}]({link_url})")

# Calculation Function
def calculate_psv(aadt_value, per_hgvs, year, lanes):
    # Reuse existing logic here
    design_period = 0 if year == 0 else (20 + 2025) - year
    result1 = per_hgvs if per_hgvs >= 11 else 11
    AADT_HGVS = result1 * (aadt_value / 100)
    total_projected_aadt_hgvs = AADT_HGVS * (1 + 1.54 / 100) ** design_period
    AADT_HGVS = round(AADT_HGVS)
    total_projected_aadt_hgvs = round(total_projected_aadt_hgvs)

    # Percentage of commercial vehicles in each lane
    lane1 = lane2 = lane3 = lane4 = 0
    lane_details_lane1 = lane_details_lane2 = lane_details_lane3 = lane_details_lane4 = 0
    if lanes == 1:
        lane1 = 100
        lane_details_lane1 = total_projected_aadt_hgvs
    elif lanes == 2:
        lane1 = round(100 - (0.0036 * total_projected_aadt_hgvs))
        lane2 = 100 - lane1
        lane_details_lane1 = round(total_projected_aadt_hgvs * (lane1 / 100))
        lane_details_lane2 = round(total_projected_aadt_hgvs * (lane2 / 100))
    elif lanes >= 3:
        # Handle 3 or 4 lanes based on the existing logic
        pass

    return AADT_HGVS, total_projected_aadt_hgvs, lane1, lane2, lane3, lane4, lane_details_lane1, lane_details_lane2, lane_details_lane3, lane_details_lane4

# Process and display results for each entry
for idx, entry in enumerate(st.session_state.entries):
    AADT_HGVS, total_projected_aadt_hgvs, lane1, lane2, lane3, lane4, lane_details_lane1, lane_details_lane2, lane_details_lane3, lane_details_lane4 = calculate_psv(entry['aadt_value'], entry['per_hgvs'], entry['year'], entry['lanes'])

    st.subheader(f"Results for Entry {idx+1}")
    st.write(f"AADT_HGVS: {AADT_HGVS}")
    st.write(f"Total Projected AADT HGVs: {total_projected_aadt_hgvs}")
    st.write(f"Lane1: {lane1}%")
    st.write(f"Lane2: {lane2}%")
    st.write(f"Lane3: {lane3}%")
    st.write(f"Lane4: {lane4}%")
    st.write(f"Lane Details Lane1: {lane_details_lane1}")
    st.write(f"Lane Details Lane2: {lane_details_lane2}")
    st.write(f"Lane Details Lane3: {lane_details_lane3}")
    st.write(f"Lane Details Lane4: {lane_details_lane4}")



