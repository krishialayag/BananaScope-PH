"""
src/data_cleaning.py
--------------------
Automated Data Cleaning & Transformation Pipeline for BananaScope PH.
Processes raw PSA OpenStat multi-year banana production records from BananaData.xlsx.
"""

import os
import re
import numpy as np
import pandas as pd


def clean_banana_dataset(
    input_path: str = "data/BananaData.xlsx",
    output_path: str = "outputs/cleaned_banana_data.csv",
    sheet_name: str = "Clean Data"
) -> pd.DataFrame:
    """
    Executes the 12-step automated cleaning and normalization pipeline.
    
    Cleaning Decisions & Methodology:
    1. Header Alignment: Identifies row index 1 as the column header row.
    2. Phantom Row Elimination: Filters out empty rows and residual '..' cells from earlier manual edits.
    3. Hierarchy Disaggregation: Parses indentation markers ('..', '....', '......') to identify
       National, Regional, and Provincial/City levels, while mapping every province to its parent region.
    4. Footnote Stripping: Uses regular expressions to clean trailing administrative footnote markers
       (e.g., 'NIR 2/', 'Sulu c/').
    5. Variety Standardization: Maps raw crop names to standardized descriptive names and adds
       an 'Is_Aggregate_Variety' flag to separate the total commodity from specific cultivars.
    6. Non-Destructive Missing Value Representation: Preserves PSA '..' notation as NaN without
       blind zero-imputation, accompanied by a 'Data_Status' audit column.
    7. Double-Counting Prevention: Unpivots wide columns into tidy rows categorized by 'Period_Type'
       ('Quarterly', 'Semester', 'Annual').
    """
    print("=" * 70)
    print(" BANANASCOPE PH: AUTOMATED DATA CLEANING & TRANSFORMATION PIPELINE")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # STEP 1: LOAD THE ORIGINAL EXCEL DATASET
    # -------------------------------------------------------------------------
    if not os.path.exists(input_path):
        # Fallback to root directory if data/ copy is not found
        if os.path.exists("BananaData.xlsx"):
            input_path = "BananaData.xlsx"
        else:
            raise FileNotFoundError(f"Input file not found at: {input_path}")

    print(f"\n[Step 1] Loading raw Excel workbook from: {input_path}")
    print(f"         Reading sheet: '{sheet_name}'...")
    
    # Load sheet without header first to inspect structure
    raw_df = pd.read_excel(input_path, sheet_name=sheet_name, header=None)
    print(f"         Raw worksheet loaded: {raw_df.shape[0]} rows, {raw_df.shape[1]} columns.")

    # -------------------------------------------------------------------------
    # STEP 2: IDENTIFY THE CORRECT HEADERS
    # -------------------------------------------------------------------------
    print("\n[Step 2] Identifying header row...")
    # Row index 0 contains the worksheet title
    # Row index 1 contains the actual column names ('Crop', 'Geolocation', '2010 Quarter1', ...)
    header_row_idx = 1
    raw_headers = raw_df.iloc[header_row_idx].tolist()
    
    # Assign headers and slice data rows
    df = raw_df.iloc[header_row_idx + 1:].copy()
    df.columns = raw_headers
    print(f"         Assigned {len(df.columns)} column headers from row {header_row_idx + 1}.")

    # -------------------------------------------------------------------------
    # STEP 3: REMOVE UNNECESSARY BLANK ROWS AND COLUMNS
    # -------------------------------------------------------------------------
    print("\n[Step 3] Removing unnecessary blank rows and phantom cells...")
    initial_rows = len(df)
    
    # Drop rows where Crop is NaN or completely empty
    df = df[df['Crop'].notna()].copy()
    
    # Drop rows where Crop is '..' (residual phantom rows from prior Excel deletions)
    df = df[df['Crop'].astype(str).str.strip() != '..'].copy()
    
    # Drop rows where Geolocation is missing
    df = df[df['Geolocation'].notna()].copy()
    
    # Drop any completely empty columns
    df = df.dropna(how='all', axis=1).copy()
    
    dropped_rows = initial_rows - len(df)
    print(f"         Dropped {dropped_rows:,} empty / phantom rows.")
    print(f"         Retained {len(df):,} valid data rows.")

    # -------------------------------------------------------------------------
    # STEP 4: STANDARDIZE COLUMN NAMES
    # -------------------------------------------------------------------------
    print("\n[Step 4] Standardizing column names...")
    cleaned_col_names = []
    for col in df.columns:
        col_str = str(col).strip()
        # Clean double spaces or newline characters
        col_str = re.sub(r'\s+', ' ', col_str)
        cleaned_col_names.append(col_str)
    df.columns = cleaned_col_names

    # -------------------------------------------------------------------------
    # STEP 5: IDENTIFY BANANA PRODUCTION RECORDS AND BANANA VARIETIES
    # -------------------------------------------------------------------------
    print("\n[Step 5] Identifying banana varieties and classifying aggregate records...")
    valid_varieties = {
        'Banana': 'Banana (Total)',
        'Banana Cavendish': 'Banana Cavendish',
        'Banana Saba': 'Banana Saba',
        'Banana Lakatan': 'Banana Lakatan',
        'Banana Latundan': 'Banana Latundan',
        'Banana Bungulan': 'Banana Bungulan',
        'Banana Others': 'Banana Others'
    }

    # Filter strictly for banana varieties
    df = df[df['Crop'].isin(valid_varieties.keys())].copy()
    df['Crop_Standardized'] = df['Crop'].map(valid_varieties)
    
    # Flag aggregate commodity totals vs. individual cultivars to avoid double-counting
    df['Is_Aggregate_Variety'] = df['Crop_Standardized'] == 'Banana (Total)'
    
    print(f"         Identified {df['Crop_Standardized'].nunique()} distinct banana categories:")
    for crop_name, count in df['Crop_Standardized'].value_counts().items():
        is_agg = "(Aggregate Total)" if crop_name == 'Banana (Total)' else "(Specific Cultivar)"
        print(f"           - {crop_name:<20}: {count} geographic observations {is_agg}")

    # -------------------------------------------------------------------------
    # STEP 6: ORGANIZE REGIONAL AND PROVINCIAL LOCATIONS (HIERARCHY PARSER)
    # -------------------------------------------------------------------------
    print("\n[Step 6] Parsing geographic hierarchy and cleaning administrative footnotes...")
    
    # We iterate down the unique geolocations in order to map each province to its parent region
    unique_geos = df['Geolocation'].unique()
    geo_metadata = {}
    current_region = "PHILIPPINES"

    for raw_geo in unique_geos:
        geo_str = str(raw_geo).strip()
        
        # Remove footnote markers like ' 1/', ' 2/', ' 3/', ' a/', ' b/', ' c/'
        clean_name = re.sub(r'\s+[0-9a-zA-Z]/$', '', geo_str).strip()
        # Remove leading period hierarchy tags for the clean name
        clean_name = re.sub(r'^[.]+ *', '', clean_name).strip()

        if geo_str == "PHILIPPINES":
            hierarchy = "National"
            region_name = "PHILIPPINES"
            province_name = "PHILIPPINES"
        elif geo_str.startswith("..") and not geo_str.startswith("...."):
            hierarchy = "Regional"
            current_region = clean_name
            region_name = clean_name
            province_name = "Regional Total"
        elif geo_str.startswith("....") and not geo_str.startswith("......"):
            hierarchy = "Provincial"
            region_name = current_region
            province_name = clean_name
        elif geo_str.startswith("......"):
            hierarchy = "City"
            region_name = current_region
            province_name = clean_name
        else:
            hierarchy = "Special / Other"
            region_name = current_region
            province_name = clean_name

        geo_metadata[raw_geo] = {
            'Hierarchy_Level': hierarchy,
            'Region': region_name,
            'Province_City': province_name
        }

    # Map parsed metadata onto the dataframe
    df['Hierarchy_Level'] = df['Geolocation'].map(lambda g: geo_metadata[g]['Hierarchy_Level'])
    df['Region'] = df['Geolocation'].map(lambda g: geo_metadata[g]['Region'])
    df['Province_City'] = df['Geolocation'].map(lambda g: geo_metadata[g]['Province_City'])

    print(f"         Organized {len(unique_geos)} geographic entities:")
    print(f"           - National Level    : {(df['Hierarchy_Level'] == 'National').sum() // 7} record(s)")
    print(f"           - Regional Level    : {(df['Hierarchy_Level'] == 'Regional').sum() // 7} administrative regions")
    print(f"           - Provincial Level  : {(df['Hierarchy_Level'] == 'Provincial').sum() // 7} provinces")
    print(f"           - City Level        : {(df['Hierarchy_Level'] == 'City').sum() // 7} independent/chartered cities")
    print(f"         Confirmed local context: Oriental Mindoro mapped under '{geo_metadata['....Oriental Mindoro']['Region']}'.")

    # -------------------------------------------------------------------------
    # STEP 7 & 10: SEPARATE TEMPORAL MEASUREMENTS & RESHAPE TO TIDY FORMAT
    # -------------------------------------------------------------------------
    print("\n[Step 7 & 10] Reshaping wide matrix into long tidy format...")
    print("              Categorizing Quarterly, Semester, and Annual metrics to prevent double counting...")

    # Identify temporal columns (exclude metadata columns)
    metadata_cols = ['Crop', 'Crop_Standardized', 'Is_Aggregate_Variety', 'Geolocation', 
                     'Hierarchy_Level', 'Region', 'Province_City']
    time_cols = [c for c in df.columns if c not in metadata_cols]

    # Melt dataframe from wide to long
    df_long = pd.melt(
        df,
        id_vars=metadata_cols,
        value_vars=time_cols,
        var_name='Raw_Time_Header',
        value_name='Raw_Value'
    )

    # Parse Year and Period from column name (e.g., '2010 Quarter1', '2015 Semester2', '2020 Annual')
    def parse_time_header(header_str):
        # Extract year (4 digits)
        year_match = re.search(r'^(20\d\d)', header_str)
        year = int(year_match.group(1)) if year_match else None
        
        # Extract period type
        if 'Quarter1' in header_str:
            period = 'Q1'
            p_type = 'Quarterly'
        elif 'Quarter2' in header_str:
            period = 'Q2'
            p_type = 'Quarterly'
        elif 'Quarter3' in header_str:
            period = 'Q3'
            p_type = 'Quarterly'
        elif 'Quarter4' in header_str:
            period = 'Q4'
            p_type = 'Quarterly'
        elif 'Semester1' in header_str:
            period = 'S1'
            p_type = 'Semester'
        elif 'Semester2' in header_str:
            period = 'S2'
            p_type = 'Semester'
        elif 'Annual' in header_str:
            period = 'Annual'
            p_type = 'Annual'
        else:
            period = header_str
            p_type = 'Other'
            
        return year, period, p_type

    time_parsed = [parse_time_header(h) for h in df_long['Raw_Time_Header']]
    df_long['Year'] = [t[0] for t in time_parsed]
    df_long['Period'] = [t[1] for t in time_parsed]
    df_long['Period_Type'] = [t[2] for t in time_parsed]

    # -------------------------------------------------------------------------
    # STEP 8: IDENTIFY MISSING VALUES & CONVERT PRODUCTION TO NUMERICAL FORMAT
    # -------------------------------------------------------------------------
    print("\n[Step 8] Auditing missing values and converting production values to numerical floats...")
    
    # Classify data status before conversion
    def classify_status(val, year, period):
        if pd.isna(val) or str(val).strip() == '':
            if year >= 2025:
                return 'Unreported / Future Template'
            return 'Missing / Blank'
        val_str = str(val).strip()
        if val_str == '..':
            return 'Not Available / Negligible'
        try:
            float(val_str.replace(',', ''))
            return 'Reported'
        except ValueError:
            return 'Inconsistent / Non-Numeric'

    df_long['Data_Status'] = [
        classify_status(val, y, p) 
        for val, y, p in zip(df_long['Raw_Value'], df_long['Year'], df_long['Period'])
    ]

    # Non-destructive conversion: convert valid numbers to float; preserve '..' and missing as NaN
    def clean_numeric(val):
        if pd.isna(val):
            return np.nan
        val_str = str(val).strip().replace(',', '')
        if val_str in ['..', '', 'nan', 'None']:
            # Do NOT replace with zero without explicit user mandate!
            return np.nan
        try:
            return float(val_str)
        except ValueError:
            return np.nan

    df_long['Volume_MT'] = df_long['Raw_Value'].apply(clean_numeric)

    status_counts = df_long['Data_Status'].value_counts()
    print("         Data Status Breakdown:")
    for status, count in status_counts.items():
        pct = (count / len(df_long)) * 100
        print(f"           - {status:<30}: {count:>7,} rows ({pct:>5.1f}%)")

    # -------------------------------------------------------------------------
    # STEP 9: CHECK FOR DUPLICATE OBSERVATIONS
    # -------------------------------------------------------------------------
    print("\n[Step 9] Checking for duplicate observations...")
    duplicate_keys = ['Year', 'Period', 'Crop_Standardized', 'Geolocation']
    duplicates_count = df_long.duplicated(subset=duplicate_keys).sum()
    print(f"         Duplicate records found across key attributes: {duplicates_count}")
    if duplicates_count > 0:
        df_long = df_long.drop_duplicates(subset=duplicate_keys, keep='first').copy()
        print(f"         Removed {duplicates_count} duplicate rows.")

    # -------------------------------------------------------------------------
    # STEP 11: GENERATE AND FINALIZE CLEANED DATASET
    # -------------------------------------------------------------------------
    print("\n[Step 11] Assembling standardized column layout...")
    final_columns = [
        'Year',
        'Period',
        'Period_Type',
        'Crop_Standardized',
        'Is_Aggregate_Variety',
        'Geolocation',
        'Hierarchy_Level',
        'Region',
        'Province_City',
        'Volume_MT',
        'Data_Status'
    ]
    
    cleaned_df = df_long[final_columns].copy()
    cleaned_df = cleaned_df.rename(columns={'Crop_Standardized': 'Crop', 'Geolocation': 'Geolocation_Raw'})
    
    # Sort chronologically and geographically
    period_sort_order = {'Q1': 1, 'Q2': 2, 'S1': 3, 'Q3': 4, 'Q4': 5, 'S2': 6, 'Annual': 7}
    cleaned_df['Period_Order'] = cleaned_df['Period'].map(period_sort_order).fillna(99)
    cleaned_df = cleaned_df.sort_values(by=['Crop', 'Region', 'Province_City', 'Year', 'Period_Order'])
    cleaned_df = cleaned_df.drop(columns=['Period_Order'])
    cleaned_df = cleaned_df.reset_index(drop=True)

    # -------------------------------------------------------------------------
    # STEP 12: SAVE THE CLEANED RESULTS IN OUTPUTS/CLEANED_BANANA_DATA.CSV
    # -------------------------------------------------------------------------
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"\n[Step 12] Saving cleaned dataset to: {output_path}")
    cleaned_df.to_csv(output_path, index=False)
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"          Successfully saved: {len(cleaned_df):,} rows ({file_size_mb:.2f} MB).")

    # Also export convenient pre-filtered splits for instant analysis
    annual_path = "outputs/cleaned_banana_annual.csv"
    quarterly_path = "outputs/cleaned_banana_quarterly.csv"
    
    cleaned_df[cleaned_df['Period_Type'] == 'Annual'].to_csv(annual_path, index=False)
    cleaned_df[cleaned_df['Period_Type'] == 'Quarterly'].to_csv(quarterly_path, index=False)
    print(f"          Convenience split saved: {annual_path} (Annual totals only, no double counting)")
    print(f"          Convenience split saved: {quarterly_path} (Quarterly metrics only for seasonality)")

    # -------------------------------------------------------------------------
    # SUMMARY VALIDATION REPORT
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print(" DATA CLEANING EXECUTION SUMMARY")
    print("=" * 70)
    print(f" Total observations generated   : {len(cleaned_df):,}")
    print(f" Calendar Years covered         : {cleaned_df['Year'].min()} to {cleaned_df['Year'].max()}")
    print(f" Unique Banana Cultivars        : {cleaned_df['Crop'].nunique()}")
    print(f" Administrative Regions         : {cleaned_df[cleaned_df['Hierarchy_Level'] == 'Regional']['Region'].nunique()}")
    print(f" Provinces & Cities             : {cleaned_df[cleaned_df['Hierarchy_Level'].isin(['Provincial', 'City'])]['Province_City'].nunique()}")
    print(f" Non-null Volume_MT records     : {cleaned_df['Volume_MT'].notna().sum():,}")
    print(f" Missing / Unrecorded records   : {cleaned_df['Volume_MT'].isna().sum():,}")
    print("=" * 70)

    return cleaned_df


if __name__ == "__main__":
    clean_banana_dataset()
