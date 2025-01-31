import streamlit as st
import pandas as pd
import math


# Function to calculate the AADT for each lane
def roundup(value):
    return math.ceil(value)
    
if uploaded_file is not None:
    # Read the Excel file into a DataFrame
    df = pd.read_excel(uploaded_file)
    
    # Clean up column names by removing leading/trailing spaces
    df.columns = df.columns.str.strip()  # This line removes any extra spaces from column names
    
    # Display the DataFrame (optional, for debugging)
    st.write(df)
    
    # Proceed with your calculation logic
    report_df = calculate_psv(df, psv_df)

# Function to perform PSV calculation based on input data
def calculate_psv(df, psv_df):
    report = []
    for idx, row in df.iterrows():
        # Extracting values from the DataFrame
        aadt_value = row['AADT']
        per_hgvs = row['% of HGVs']
        year = row['Year']
        lanes = row['Number of Lanes']
        site_category = row['Site Category']
        il_value = row['IL Value']

        # Calculating Design Period
        if year == 0:
            design_period = 0
        else:
            design_period = ((20 + 2025) - year)

        # AADT HGV calculation
        if per_hgvs >= 11:
            result1 = per_hgvs
            AADT_HGVS = (result1 * (aadt_value / 100))
        else:
            result2 = 11
            AADT_HGVS = ((result2 * aadt_value) / 100)

        total_projected_aadt_hgvs = (AADT_HGVS * (1 + 1.54 / 100) ** design_period)
        AADT_HGVS = roundup(AADT_HGVS)
        total_projected_aadt_hgvs = roundup(total_projected_aadt_hgvs)

        # Percentage of commercial vehicles in each lane
        lane1 = lane2 = lane3 = lane4 = 0
        lane_details_lane1 = lane_details_lane2 = lane_details_lane3 = lane_details_lane4 = 0

        if lanes == 1:
            lane1 = 100
            lane_details_lane1 = total_projected_aadt_hgvs
        elif lanes > 1 and lanes <= 3:
            if total_projected_aadt_hgvs < 5000:
                lane1 = round(100 - (0.0036 * total_projected_aadt_hgvs))
                lane2 = round(100 - lane1)
            elif 5000 <= total_projected_aadt_hgvs < 25000:
                lane1 = round(89 - (0.0014 * total_projected_aadt_hgvs))
                lane2 = 100 - lane1
            else:
                lane1 = 54
                lane2 = 100 - 54
                lane3 = 0
            lane_details_lane1 = round(total_projected_aadt_hgvs * (lane1 / 100))
            lane_details_lane2 = round(total_projected_aadt_hgvs * (lane2 / 100))

        elif lanes >= 4:
            if total_projected_aadt_hgvs <= 10500:
                lane1 = round(100 - (0.0036 * total_projected_aadt_hgvs))
                lane_2_3 = (total_projected_aadt_hgvs - ((total_projected_aadt_hgvs * lane1) / 100))
                lane2 = round(89 - (0.0014 * lane_2_3))
                lane3 = 100 - lane2
                lane4 = 0
            elif 10500 < total_projected_aadt_hgvs < 25000:
                lane1 = round(75 - (0.0012 * total_projected_aadt_hgvs))
                lane_2_3 = (total_projected_aadt_hgvs - ((total_projected_aadt_hgvs * lane1) / 100))
                lane2 = round(89 - (0.0014 * lane_2_3))
                lane3 = 100 - lane2
                lane4 = 0
            else:
                lane1 = 45
                lane2 = 54
                lane3 = 100 - 54
            lane_details_lane1 = round(total_projected_aadt_hgvs * (lane1 / 100))
            lane_details_lane2 = round((total_projected_aadt_hgvs - lane_details_lane1) * (lane2 / 100))
            lane_details_lane3 = round(total_projected_aadt_hgvs - (lane_details_lane1 + lane_details_lane2))

        # Look-up PSV from uploaded table
        range_column = None
        for col in psv_df.columns:
            if '-' in col:
                col_range = list(map(int, col.split('-')))
                if col_range[0] <= lane_details_lane1 <= col_range[1]:
                    range_column = col
                    break

        if range_column:
            # Filter the DataFrame based on input values
            filtered_df = psv_df[(psv_df['SiteCategory'] == site_category) & (psv_df['IL'] == il_value)]
            if not filtered_df.empty:
                psv_lane1 = filtered_df.iloc[0][range_column]
            else:
                psv_lane1 = "No matching result found."
        else:
            psv_lane1 = "No matching range found for the given value."

        # Storing report data
        report.append({
            'Section Number': row['Link Section Number'],
            'AADT HGVS': AADT_HGVS,
            'Design Period': design_period,
            'Total Projected AADT HGVS': total_projected_aadt_hgvs,
            'Lane1 %': lane1,
            'Lane2 %': lane2,
            'Lane3 %': lane3,
            'Lane4 %': lane4,
            'Lane Details Lane1': lane_details_lane1,
            'Lane Details Lane2': lane_details_lane2,
            'Lane Details Lane3': lane_details_lane3,
            'Lane Details Lane4': lane_details_lane4,
            'PSV Lane1': psv_lane1
        })

    # Convert the report data into a DataFrame
    report_df = pd.DataFrame(report)
    return report_df

# Streamlit UI
st.title("Polished Stone Value (PSV) Report Generator")

# Upload Excel File with Link Section Data
uploaded_file = st.file_uploader("Upload Excel file with Link Section Details", type=["xlsx"])

# Upload PSV Lookup Table
psv_table = st.file_uploader("Upload PSV Lookup Table", type=["xlsx"])

# If both files are uploaded
if uploaded_file is not None and psv_table is not None:
    # Read the data files into DataFrames
    df = pd.read_excel(uploaded_file)
    psv_df = pd.read_excel(psv_table)

    # Display the uploaded data
    st.write("Uploaded Link Section Data:")
    st.write(df)
    st.write("Uploaded PSV Table:")
    st.write(psv_df)

    # Calculate PSV based on the uploaded data
    report_df = calculate_psv(df, psv_df)

    # Display the report in a table format
    st.write("PSV Calculation Report:")
    st.write(report_df)

    # Provide a download button for the report
    st.download_button(
        label="Download Report as Excel",
        data=report_df.to_excel(index=False),
        file_name="PSV_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.write("Please upload both the Link Section Data and PSV Lookup Table to generate the report.")
