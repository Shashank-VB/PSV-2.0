import streamlit as st
import pandas as pd
import math

# Title
st.title("Polished Stone Value (PSV) Calculator Results")

# Sidebar for inputs
st.sidebar.title("PSV Calculator Inputs")
st.sidebar.header("Enter values:")
link_section_number = st.sidebar.text_input("Enter Link Section Number:", "")
aadt_value = st.sidebar.number_input("Enter AADT value:", min_value=0)
per_hgvs = st.sidebar.number_input("Enter % of HGVs:")
year = st.sidebar.number_input("Enter Year", min_value=0)
lanes = st.sidebar.number_input("Enter number of Lanes", min_value=1)
il_value = st.sidebar.number_input("Enter IL value:")
site_category = st.sidebar.text_input("Enter Site Category:")

# Initialize session state for entries
if 'entries' not in st.session_state:
    st.session_state.entries = {}

# Add Entry button to add more entries
if st.sidebar.button("Add Link Section"):
    if link_section_number:
        entry_data = {
            'aadt_value': aadt_value,
            'per_hgvs': per_hgvs,
            'year': year,
            'lanes': lanes,
            'il_value': il_value,
            'site_category': site_category
        }
        st.session_state.entries[link_section_number] = entry_data
    else:
        st.error("Please enter a valid link section number.")

# Excel file uploader for PSV values
st.sidebar.header("Upload PSV Excel File")
uploaded_file = st.sidebar.file_uploader("Upload your Excel file:", type=["xlsx"])

df = None
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.sidebar.error(f"Error reading file: {str(e)}")

def calculate_psv(aadt_value, per_hgvs, year, lanes):
    design_period = 0 if year == 0 else ((20 + 2025) - year)
    result1 = max(per_hgvs, 11)
    AADT_HGVS = round((result1 * (aadt_value / 100)))
    total_projected_aadt_hgvs = round(AADT_HGVS * (1 + 1.54 / 100) ** design_period)
    
    lane_distribution = [0] * 4
    lane_details = [0] * 4
    
    if lanes == 1:
        lane_distribution[0] = 100
        lane_details[0] = total_projected_aadt_hgvs
    elif lanes <= 3:
        lane_distribution[0] = max(54, 89 - (0.0014 * total_projected_aadt_hgvs))
        lane_distribution[1] = 100 - lane_distribution[0]
    elif lanes >= 4:
        lane_distribution[0] = max(45, 75 - (0.0012 * total_projected_aadt_hgvs))
        lane_distribution[1] = max(54, 89 - (0.0014 * total_projected_aadt_hgvs))
        lane_distribution[2] = 100 - lane_distribution[1]
    
    for i in range(4):
        lane_details[i] = round(total_projected_aadt_hgvs * (lane_distribution[i] / 100))
    
    return AADT_HGVS, total_projected_aadt_hgvs, lane_distribution, lane_details, design_period

def get_psv_for_lane(df, value1, value2, lane_value):
    if lane_value == 0:
        return "NA"
    for col in df.columns:
        if '-' in str(col):
            col_range = list(map(int, str(col).split('-')))
            if col_range[0] <= lane_value <= col_range[1]:
                filtered_df = df[(df['SiteCategory'] == value1) & (df['IL'] == value2)]
                return filtered_df.iloc[0][col] if not filtered_df.empty else "No matching result found."
    return "No matching range found."

# Display calculated results
for link_section_number, entry in st.session_state.entries.items():
    with st.expander(f"Link Section: {link_section_number}", expanded=True):
        AADT_HGVS, total_projected_aadt_hgvs, lane_distribution, lane_details, design_period = calculate_psv(
            entry['aadt_value'], entry['per_hgvs'], entry['year'], entry['lanes']
        )
        
        st.subheader("Traffic Calculations")
        st.write(f"AADT_HGVS: {AADT_HGVS}")
        st.write(f"Total Projected AADT HGVs: {total_projected_aadt_hgvs}")
        
        st.subheader("Lane Distribution (%)")
        for i, lane in enumerate(lane_distribution, 1):
            st.write(f"Lane{i}: {lane}%")
        
        st.subheader("Lane Traffic Details")
        for i, lane in enumerate(lane_details, 1):
            st.write(f"Lane Details Lane{i}: {lane}")
        
        if uploaded_file is not None:
            st.subheader("PSV Values")
            for i, lane in enumerate(lane_details, 1):
                st.write(f"PSV at Lane{i}: {get_psv_for_lane(df, entry['site_category'], entry['il_value'], lane)}")
