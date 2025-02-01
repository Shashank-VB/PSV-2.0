import streamlit as st
import pandas as pd
import math

# Title
st.title("Polished Stone Value (PSV) Calculator Results")

# Sidebar for inputs
st.sidebar.title("Polished Stone Value (PSV) Calculator")
st.sidebar.header("Enter values:")
link_section_number = st.sidebar.text_input("Enter Link Section Number:", "")  # Allow any characters
aadt_value = st.sidebar.number_input("Enter AADT value:", min_value=0)
per_hgvs = st.sidebar.number_input("Enter % of HGVs:")
year = st.sidebar.number_input("Enter Year", min_value=0)
lanes = st.sidebar.number_input("Enter number of Lanes", min_value=1)
il_value = st.sidebar.number_input("Enter IL value:")
site_category = st.sidebar.text_input("Enter Site Category:")

# Initialize session state for entries if it doesn't exist
if 'entries' not in st.session_state:
    st.session_state.entries = {}

# Add Entry button to add more entries
if st.sidebar.button("Add Link Section"):
    # Store entry with custom link section number as the key
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

# Read the Excel file if uploaded
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.sidebar.write("Excel Table Preview:")
    st.sidebar.write(df.head())  # Show preview of the table

# Function to calculate AADT_HGVS and design period
def calculate_psv(aadt_value, per_hgvs, year, lanes):
    # Default values for lanes
    lane1 = lane2 = lane3 = lane4 = 0
    lane_details_lane1 = lane_details_lane2 = lane_details_lane3 = lane_details_lane4 = 0
    design_period = 0 if year == 0 else ((20 + 2025) - year)
    
    
    # Calculate AADT of HGVS
    result1 = per_hgvs if per_hgvs >= 11 else 11
    AADT_HGVS = (result1 * (aadt_value / 100))
    total_projected_aadt_hgvs = (AADT_HGVS * (1 + 1.54 / 100) ** design_period)
    AADT_HGVS = round(AADT_HGVS)
    total_projected_aadt_hgvs = round(total_projected_aadt_hgvs)
    
  
    # percentage of commercial vehicles in each lane
    if lanes == 1:
        lane1 = 100
        lane_details_lane1 = total_projected_aadt_hgvs
    elif lanes > 1 and lanes <= 3:
        if total_projected_aadt_hgvs < 5000:
            lane1 =  math.ceil(100 - (0.0036 * total_projected_aadt_hgvs))
            lane2 =  math.ceil(100 - lane1)
        elif 5000 <= total_projected_aadt_hgvs < 25000:
            lane1 =  math.ceil(89 - (0.0014 * total_projected_aadt_hgvs))
            lane2 = 100 - lane1
        else:
            lane1 = 54
            lane2 = 100 - 54
        lane_details_lane1 =  math.ceil(total_projected_aadt_hgvs * (lane1 / 100))
        lane_details_lane2 =  math.ceil(total_projected_aadt_hgvs * (lane2 / 100))
    elif lanes >= 4:
        if total_projected_aadt_hgvs <= 10500:
            lane1 =  math.ceil(100 - (0.0036 * total_projected_aadt_hgvs))
            lane_2_3 = total_projected_aadt_hgvs - ((total_projected_aadt_hgvs * lane1) / 100)
            lane2 =  math.ceil(89 - (0.0014 * lane_2_3))
            lane3 = 100 - lane2
        elif 10500 < total_projected_aadt_hgvs < 25000:
            lane1 =  math.ceil(75 - (0.0012 * total_projected_aadt_hgvs))
            lane_2_3 = total_projected_aadt_hgvs - ((total_projected_aadt_hgvs * lane1) / 100)
            lane2 =  math.ceil(89 - (0.0014 * lane_2_3))
            lane3 = 100 - lane2
        else:
            lane1 = 45
            lane2 = 54
            lane3 = 100 - 54
        lane_details_lane1 =  math.ceil(total_projected_aadt_hgvs * (lane1 / 100))
        lane_details_lane2 =  math.ceil((total_projected_aadt_hgvs - lane_details_lane1) * (lane2 / 100))
        lane_details_lane3 =  math.ceil(total_projected_aadt_hgvs - (lane_details_lane1 + lane_details_lane2))

    return AADT_HGVS, total_projected_aadt_hgvs, lane1, lane2, lane3, lane4, lane_details_lane1, lane_details_lane2, lane_details_lane3, lane_details_lane4

# Loop over each entry and calculate results
for link_section_number, entry in st.session_state.entries.items():
    with st.expander(f"Link Section: {link_section_number}"):
        AADT_HGVS, total_projected_aadt_hgvs, lane1, lane2, lane3, lane4, lane_details_lane1, lane_details_lane2, lane_details_lane3, lane_details_lane4 = calculate_psv(
            entry['aadt_value'], entry['per_hgvs'], entry['year'], entry['lanes']
        )

        # Loop over each entry and calculate results
for link_section_number, entry in st.session_state.entries.items():
    with st.expander(f"Link Section: {link_section_number}"):
        # Calculate values
        AADT_HGVS, total_projected_aadt_hgvs, lane1, lane2, lane3, lane4, lane_details_lane1, lane_details_lane2, lane_details_lane3, lane_details_lane4, design_period = calculate_psv(
            entry['aadt_value'], entry['per_hgvs'], entry['year'], entry['lanes']
        )

        st.subheader("Generic")
        st.write(f"AADT_HGVS: {AADT_HGVS}")
        st.write(f"Design Period in years: {design_period}")
        st.write(f"Total Projected AADT HGVs: {total_projected_aadt_hgvs}")

        st.subheader("Percentage of CVs in Each Lane")
        st.write(f"Lane1: {lane1}%")
        st.write(f"Lane2: {lane2}%")
        st.write(f"Lane3: {lane3}%")
        st.write(f"Lane4: {lane4}%")

        st.subheader("Design Traffic")
        st.write(f"Lane Details Lane1: {lane_details_lane1}")
        st.write(f"Lane Details Lane2: {lane_details_lane2}")
        st.write(f"Lane Details Lane3: {lane_details_lane3}")
        st.write(f"Lane Details Lane4: {lane_details_lane4}")

        # PSV Calculations (only if file is uploaded)
        if df is not None:
            value1 = entry['site_category']
            value2 = entry['il_value']
            value3 = lane_details_lane1
            value4 = lane_details_lane2
            value5 = lane_details_lane3

            def get_psv_for_lane(df, value1, value2, lane_value):
                if lane_value == 0:
                    return "NA"
                range_column = None
                for col in df.columns:
                    if '-' in col:
                        col_range = list(map(int, col.split('-')))
                        if col_range[0] <= lane_value <= col_range[1]:
                            range_column = col
                            break
                if range_column:
                    filtered_df = df[(df['SiteCategory'] == value1) & (df['IL'] == value2)]
                    if not filtered_df.empty:
                        return filtered_df.iloc[0][range_column]
                    else:
                        return "No matching result found."
                else:
                    return "No matching range found for the given value."

            st.subheader("Min. PSV Values at Each Lane")
            st.write(f"PSV at Lane1: {get_psv_for_lane(df, value1, value2, value3)}")
            st.write(f"PSV at Lane2: {get_psv_for_lane(df, value1, value2, value4)}")
            st.write(f"PSV at Lane3: {get_psv_for_lane(df, value1, value2, value5)}")
        else:
            st.warning("Upload an Excel file to calculate PSV values.")
