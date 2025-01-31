import streamlit as st
import pandas as pd
import math
from openpyxl import load_workbook

# Title
st.title("Polished Stone Value (PSV) Batch Calculator")

# File Upload
st.sidebar.header("Upload Excel File")
uploaded_file = st.sidebar.file_uploader("Upload your Excel file:", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    
    # Ensure required columns exist
    required_columns = {"AADT", "%HGVs", "Year", "Lanes", "SiteCategory", "IL"}
    if not required_columns.issubset(df.columns):
        st.error(f"Missing required columns: {required_columns - set(df.columns)}")
    else:
        # Function to perform calculations
        def calculate_psv(row):
            aadt_value = row["AADT"]
            per_hgvs = row["%HGVs"]
            year = row["Year"]
            lanes = row["Lanes"]
            site_category = row["SiteCategory"]
            il_value = row["IL"]
            
            design_period = ((20 + 2025) - year) if year != 0 else 0
            aadt_hgvs = max(11, per_hgvs) * (aadt_value / 100)
            total_projected_aadt_hgvs = round(aadt_hgvs * (1 + 1.54 / 100) ** design_period)
            
            lane_distribution = [0, 0, 0, 0]  # Default for up to 4 lanes
            
            if lanes == 1:
                lane_distribution[0] = 100
            elif lanes == 2 or lanes == 3:
                lane_distribution[0] = round(100 - (0.0036 * total_projected_aadt_hgvs))
                lane_distribution[1] = 100 - lane_distribution[0]
            elif lanes >= 4:
                lane_distribution[0] = round(75 - (0.0012 * total_projected_aadt_hgvs))
                lane_distribution[1] = round(89 - (0.0014 * (total_projected_aadt_hgvs - ((total_projected_aadt_hgvs * lane_distribution[0]) / 100))))
                lane_distribution[2] = 100 - lane_distribution[1]
            
            lane_traffic = [round(total_projected_aadt_hgvs * (lane_distribution[i] / 100)) for i in range(4)]
            
            return [design_period, total_projected_aadt_hgvs] + lane_traffic
        
        # Apply calculations to each row
        results = df.apply(calculate_psv, axis=1, result_type='expand')
        results.columns = ["Design Period", "Total Projected AADT HGVs", "Lane1 Traffic", "Lane2 Traffic", "Lane3 Traffic", "Lane4 Traffic"]
        output_df = pd.concat([df, results], axis=1)
        
        # Save to a new sheet in the uploaded file
        output_filename = "Processed_" + uploaded_file.name
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Input Data', index=False)
            output_df.to_excel(writer, sheet_name='Results', index=False)
        
        st.success("Calculation complete. Download the results below.")
        st.download_button(label="Download Results", data=open(output_filename, "rb").read(), file_name=output_filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

