import streamlit as st
import pandas as pd
import math

# Configure the page
st.set_page_config(layout="wide")

# Title with custom formatting
st.markdown("# Polished Stone Value (PSV) Calculator Results")
st.markdown("---")  # Add a horizontal line for separation

# Sidebar for inputs
with st.sidebar:
    st.title("PSV Calculator Inputs")
    st.markdown("---")
    
    link_section_number = st.text_input("Enter Link Section Number:", "")
    aadt_value = st.number_input("Enter AADT value:", min_value=0)
    per_hgvs = st.number_input("Enter % of HGVs:")
    year = st.number_input("Enter Year", min_value=0)
    lanes = st.number_input("Enter number of Lanes", min_value=1)
    il_value = st.number_input("Enter IL value:")
    site_category = st.text_input("Enter Site Category:")

# Initialize session state for entries if it doesn't exist
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
        st.success(f"Added Link Section: {link_section_number}")
    else:
        st.error("Please enter a valid link section number.")

# Excel file uploader for PSV values
st.sidebar.markdown("---")
st.sidebar.header("Upload PSV Excel File")
uploaded_file = st.sidebar.file_uploader("Upload your Excel file:", type=["xlsx"])

# Read the Excel file if uploaded
df = None
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.sidebar.success("File uploaded successfully!")
        st.sidebar.dataframe(df.head())
    except Exception as e:
        st.sidebar.error(f"Error reading file: {str(e)}")

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
            lane1 = math.ceil(100 - (0.0036 * total_projected_aadt_hgvs))
            lane2 = math.ceil(100 - lane1)
        elif 5000 <= total_projected_aadt_hgvs < 25000:
            lane1 = math.ceil(89 - (0.0014 * total_projected_aadt_hgvs))
            lane2 = 100 - lane1
        else:
            lane1 = 54
            lane2 = 100 - 54
        lane_details_lane1 = math.ceil(total_projected_aadt_hgvs * (lane1 / 100))
        lane_details_lane2 = math.ceil(total_projected_aadt_hgvs * (lane2 / 100))
    elif lanes >= 4:
        if total_projected_aadt_hgvs <= 10500:
            lane1 = math.ceil(100 - (0.0036 * total_projected_aadt_hgvs))
            lane_2_3 = total_projected_aadt_hgvs - ((total_projected_aadt_hgvs * lane1) / 100)
            lane2 = math.ceil(89 - (0.0014 * lane_2_3))
            lane3 = 100 - lane2
        elif 10500 < total_projected_aadt_hgvs < 25000:
            lane1 = math.ceil(75 - (0.0012 * total_projected_aadt_hgvs))
            lane_2_3 = total_projected_aadt_hgvs - ((total_projected_aadt_hgvs * lane1) / 100)
            lane2 = math.ceil(89 - (0.0014 * lane_2_3))
            lane3 = 100 - lane2
        else:
            lane1 = 45
            lane2 = 54
            lane3 = 100 - 54
        lane_details_lane1 = math.ceil(total_projected_aadt_hgvs * (lane1 / 100))
        lane_details_lane2 = math.ceil((total_projected_aadt_hgvs - lane_details_lane1) * (lane2 / 100))
        lane_details_lane3 = math.ceil(total_projected_aadt_hgvs - (lane_details_lane1 + lane_details_lane2))

    return AADT_HGVS, total_projected_aadt_hgvs, lane1, lane2, lane3, lane4, lane_details_lane1, lane_details_lane2, lane_details_lane3, lane_details_lane4, design_period

def get_psv_for_lane(df, value1, value2, lane_value):
    if lane_value == 0:
        return "NA"
    range_column = None
    for col in df.columns:
        if '-' in str(col):
            col_range = list(map(int, str(col).split('-')))
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

# Main content area
if st.session_state.entries:
    st.markdown("## Results")
    st.markdown("---")
    
    # Loop over each entry and calculate results
    for link_section_number, entry in st.session_state.entries.items():
        with st.expander(f"Link Section: {link_section_number}", expanded=True):
            AADT_HGVS, total_projected_aadt_hgvs, lane1, lane2, lane3, lane4, lane_details_lane1, lane_details_lane2, lane_details_lane3, lane_details_lane4, design_period = calculate_psv(
                entry['aadt_value'], entry['per_hgvs'], entry['year'], entry['lanes']
            )
            
            # Generic Results Section
            st.markdown("### Generic Results")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("AADT_HGVS", f"{AADT_HGVS:,}")
            with col2:
                st.metric("Design Period (years)", f"{design_period}")
            with col3:
                st.metric("Total Projected AADT HGVs", f"{total_projected_aadt_hgvs:,}")
            
            st.markdown("---")

            # Percentage of CV's Section
            st.markdown("### Percentage of CV's in each lane")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Lane 1", f"{lane1}%")
            with col2:
                st.metric("Lane 2", f"{lane2}%")
            with col3:
                st.metric("Lane 3", f"{lane3}%")
            with col4:
                st.metric("Lane 4", f"{lane4}%")
            
            st.markdown("---")

            # Design Traffic Section
            st.markdown("### Design Traffic")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Lane 1 Traffic", f"{lane_details_lane1:,}")
            with col2:
                st.metric("Lane 2 Traffic", f"{lane_details_lane2:,}")
            with col3:
                st.metric("Lane 3 Traffic", f"{lane_details_lane3:,}")
            with col4:
                st.metric("Lane 4 Traffic", f"{lane_details_lane4:,}")
            
            # PSV Values Section
            if uploaded_file is not None and df is not None:
                st.markdown("---")
                st.markdown("### Min.PSV Values at each lane")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("PSV at Lane 1", 
                             get_psv_for_lane(df, entry['site_category'], entry['il_value'], lane_details_lane1))
                with col2:
                    st.metric("PSV at Lane 2",
                             get_psv_for_lane(df, entry['site_category'], entry['il_value'], lane_details_lane2))
                with col3:
                    st.metric("PSV at Lane 3",
                             get_psv_for_lane(df, entry['site_category'], entry['il_value'], lane_details_lane3))
else:
    st.info("Add a link section using the sidebar to see results.")
