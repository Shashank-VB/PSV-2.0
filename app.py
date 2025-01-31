import streamlit as st
import math
import pandas as pd

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
        'lanes': 1,
        'il_value': 0,
        'site_category': ""
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
        entry['il_value'] = st.number_input(f"Enter IL value for Entry {idx+1}:", key=f"il_value_{idx}")
        entry['site_category'] = st.text_input(f"Enter Site Category for Entry {idx+1}:", key=f"site_category_{idx}")

# Calculation Function
def calculate_psv(aadt_value, per_hgvs, year, lanes):
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

# Load and read the Excel file
st.sidebar.header("Upload CD 236 Excel file with table")
uploaded_file = st.sidebar.file_uploader("Upload your Excel file:", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Display the data in the uploaded Excel file
    st.write("Uploaded Table")
    st.write(df)

    # For each entry, calculate PSV values based on the Excel data
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

        # Now calculate PSV for each lane from the Excel sheet
        value1 = entry['site_category']
        value2 = entry['il_value']
        value3 = lane_details_lane1
        value4 = lane_details_lane2
        value5 = lane_details_lane3
        
        # Search and match the PSV values from the Excel sheet for each lane
        if st.sidebar.button("Search PSV"):
            # For Lane 1
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
