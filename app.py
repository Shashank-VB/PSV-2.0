import streamlit as st
import streamlit as st
import pandas as pd
import math

# Your other imports and code here

# Initialize session state for entries if it doesn't exist
if 'entries' not in st.session_state:
    st.session_state.entries = []

# The rest of your code continues...




# Initialize session state for entries if it doesn't exist
if 'entries' not in st.session_state:
    st.session_state.entries = []

# Add a new entry for each form submission
if st.sidebar.button("Add Entry"):
    st.session_state.entries.append({'aadt_value': 0, 'per_hgvs': 0, 'year': 0, 'lanes': 1, 'il_value': 0, 'site_category': ""})

# Loop over the entries to show input fields and process them
for idx, entry in enumerate(st.session_state.entries):
    with st.sidebar.expander(f"Entry {idx+1}"):
        entry['aadt_value'] = st.number_input(f"Enter AADT value for Entry {idx+1}:", min_value=0, key=f"aadt_{idx}")
        entry['per_hgvs'] = st.number_input(f"Enter % of HGVs for Entry {idx+1}:", key=f"per_hgvs_{idx}")
        entry['year'] = st.number_input(f"Enter Year for Entry {idx+1}:", min_value=0, key=f"year_{idx}")
        entry['lanes'] = st.number_input(f"Enter number of lanes for Entry {idx+1}:", min_value=1, key=f"lanes_{idx}")
        entry['il_value'] = st.number_input(f"Enter IL value for Entry {idx+1}:", key=f"il_value_{idx}")
        entry['site_category'] = st.text_input(f"Enter Site Category for Entry {idx+1}:", key=f"site_category_{idx}")

    # Ensure the button has a unique key for each entry
    if st.sidebar.button(f"Search PSV for Entry {idx+1}", key=f"search_psv_{idx}"):
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

        # Now calculate PSV for each lane from the Excel sheet
        value1 = entry['site_category']
        value2 = entry['il_value']
        value3 = lane_details_lane1
        value4 = lane_details_lane2
        value5 = lane_details_lane3
        
        # Search and match the PSV values from the Excel sheet for each lane
        range_column = None
        for col in df.columns:
            if '-' in col:
                col_range = list(map(int, col.split('-')))
                if col_range[0] <= value3 <= col_range[1]:
                    range_column = col
                    break
        if range_column:
            filtered_df = df[(df['SiteCategory'] == value1) & (df['IL'] == value2)]
            if not filtered_df.empty:
                result = filtered_df.iloc[0][range_column]
            else:
                result = "No matching result found."
        else:
            result = "No matching range found for the given value."

        st.write(f"PSV at Lane1: {result}")
        
        # For Lane 2
        if value4 == 0:
            st.write(f"Lane2: NA")
        else:
            range_column = None
            for col in df.columns:
                if '-' in col:
                    col_range = list(map(int, col.split('-')))
                    if col_range[0] <= value4 <= col_range[1]:
                        range_column = col
                        break
            if range_column:
                filtered_df = df[(df['SiteCategory'] == value1) & (df['IL'] == value2)]
                if not filtered_df.empty:
                    result2 = filtered_df.iloc[0][range_column]
                else:
                    result2 = "No matching result found."
            else:
                result2 = "No matching range found for the given value."
            st.write(f"PSV at Lane2: {result2}")

        # For Lane 3
        if value5 == 0:
            st.write(f"Lane3: NA")
        else:
            range_column = None
            for col in df.columns:
                if '-' in col:
                    col_range = list(map(int, col.split('-')))
                    if col_range[0] <= value5 <= col_range[1]:
                        range_column = col
                        break
            if range_column:
                filtered_df = df[(df['SiteCategory'] == value1) & (df['IL'] == value2)]
                if not filtered_df.empty:
                    result3 = filtered_df.iloc[0][range_column]
                else:
                    result3 = "No matching result found."
            else:
                result3 = "No matching range found for the given value."
            st.write(f"PSV at Lane3: {result3}")
