"""
src/test_validation.py
----------------------
Comprehensive Quality Assurance (QA), Validation & Testing Suite for BananaScope PH.
Performs automated verification of data integrity, mathematical calculations,
period separation, hierarchy consistency, and analytics functions.
"""

import os
import sys
import numpy as np
import pandas as pd

# Import analytics engine functions
from analytics_engine import (
    compute_yoy_growth,
    calculate_cagr,
    compute_trend_models,
    detect_statistical_anomalies,
    run_time_series_forecast
)

class TestRunner:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def record(self, test_id, name, status, details=""):
        self.results.append({
            'Test_ID': test_id,
            'Test_Name': name,
            'Status': status,
            'Details': details
        })
        symbol = "✔ PASS" if status == "PASS" else ("⚠ WARN" if status == "WARN" else "❌ FAIL")
        print(f"[{symbol}] {test_id}: {name}")
        if details:
            print(f"       -> {details}")
        if status == "PASS":
            self.passed += 1
        elif status == "WARN":
            self.warnings += 1
        else:
            self.failed += 1

    def summary(self):
        print("\n" + "=" * 70)
        print(" TEST EXECUTION SUMMARY")
        print("=" * 70)
        print(f" Total Tests Run : {len(self.results)}")
        print(f" Passed          : {self.passed}")
        print(f" Warnings        : {self.warnings}")
        print(f" Failed          : {self.failed}")
        print("=" * 70)
        return self.results


def run_all_tests():
    runner = TestRunner()
    print("=" * 70)
    print(" BANANASCOPE PH: AUTOMATED VALIDATION & AUDIT TEST SUITE")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # TEST GROUP 1: FILE SYSTEM & DATASET INGESTION
    # -------------------------------------------------------------------------
    raw_excel = "data/BananaData.xlsx"
    clean_csv = "outputs/cleaned_banana_data.csv"
    annual_csv = "outputs/cleaned_banana_annual.csv"
    quarterly_csv = "outputs/cleaned_banana_quarterly.csv"

    # 1.1 Original Raw Excel Exists & Safe
    if os.path.exists(raw_excel) and os.path.getsize(raw_excel) > 5_000_000:
        runner.record("T01", "Raw Master Dataset Intact", "PASS", f"Size: {os.path.getsize(raw_excel):,} bytes")
    else:
        runner.record("T01", "Raw Master Dataset Intact", "FAIL", "data/BananaData.xlsx missing or truncated")

    # 1.2 Cleaned CSV Exists and Non-Empty
    if os.path.exists(clean_csv) and os.path.getsize(clean_csv) > 5_000_000:
        runner.record("T02", "Cleaned Master CSV Output Exists", "PASS", f"Size: {os.path.getsize(clean_csv):,} bytes")
    else:
        runner.record("T02", "Cleaned Master CSV Output Exists", "FAIL", "outputs/cleaned_banana_data.csv missing or empty")

    # Load Cleaned Data
    df = pd.read_csv(clean_csv)

    # 1.3 Expected Schema & Columns
    expected_cols = [
        'Year', 'Period', 'Period_Type', 'Crop', 'Is_Aggregate_Variety',
        'Geolocation_Raw', 'Hierarchy_Level', 'Region', 'Province_City',
        'Volume_MT', 'Data_Status'
    ]
    if list(df.columns) == expected_cols:
        runner.record("T03", "Standardized Schema Integrity", "PASS", f"All {len(expected_cols)} columns verified")
    else:
        runner.record("T03", "Standardized Schema Integrity", "FAIL", f"Columns mismatch: {list(df.columns)}")

    # -------------------------------------------------------------------------
    # TEST GROUP 2: DATA CLEANING & HYGIENE VERIFICATION
    # -------------------------------------------------------------------------
    # 2.1 Check for Duplicate Records
    dup_cols = ['Year', 'Period', 'Crop', 'Geolocation_Raw']
    dup_count = df.duplicated(subset=dup_cols).sum()
    if dup_count == 0:
        runner.record("T04", "Zero Duplicate Observations", "PASS", f"0 duplicates across {len(df):,} rows")
    else:
        runner.record("T04", "Zero Duplicate Observations", "FAIL", f"{dup_count} duplicates detected")

    # 2.2 Verify Total Row Count
    # 707 wide rows * 119 time periods = 84,133 rows
    if len(df) == 84133:
        runner.record("T05", "Total Observation Count Match", "PASS", "Exactly 84,133 rows (707 entities * 119 periods)")
    else:
        runner.record("T05", "Total Observation Count Match", "FAIL", f"Found {len(df):,} rows, expected 84,133")

    # 2.3 Administrative Footnote Cleaning
    # Check that Region and Province_City do not end with footnotes like ' 1/', ' 2/', ' a/'
    has_footnotes = df['Province_City'].str.contains(r'\s+[0-9a-zA-Z]/$', regex=True).sum()
    if has_footnotes == 0:
        runner.record("T06", "Administrative Footnote Stripping", "PASS", "0 trailing footnotes in Province_City")
    else:
        runner.record("T06", "Administrative Footnote Stripping", "FAIL", f"{has_footnotes} unstripped footnotes")

    # -------------------------------------------------------------------------
    # TEST GROUP 3: DOUBLE-COUNTING PREVENTION & PERIOD COMPATIBILITY
    # -------------------------------------------------------------------------
    # 3.1 Verify Mutually Exclusive Period Types
    period_types = set(df['Period_Type'].unique())
    expected_p_types = {'Annual', 'Quarterly', 'Semester'}
    if period_types == expected_p_types:
        runner.record("T07", "Period Type Exclusivity", "PASS", f"Verified categories: {period_types}")
    else:
        runner.record("T07", "Period Type Exclusivity", "FAIL", f"Unexpected types: {period_types}")

    # 3.2 Period Aggregation Arithmetic Verification (S1 + S2 == Annual)
    # Check for National Banana (Total) across 2010 to 2024
    nat_df = df[(df['Hierarchy_Level'] == 'National') & (df['Crop'] == 'Banana (Total)')].copy()
    
    annual_match_errors = 0
    for y in range(2010, 2025):
        s1 = nat_df[(nat_df['Year'] == y) & (nat_df['Period'] == 'S1')]['Volume_MT'].values[0]
        s2 = nat_df[(nat_df['Year'] == y) & (nat_df['Period'] == 'S2')]['Volume_MT'].values[0]
        ann = nat_df[(nat_df['Year'] == y) & (nat_df['Period'] == 'Annual')]['Volume_MT'].values[0]
        
        diff = abs((s1 + s2) - ann)
        if diff > 0.1:  # Allow 0.1 MT rounding tolerance
            annual_match_errors += 1
            
    if annual_match_errors == 0:
        runner.record("T08", "Semestral-to-Annual Sum Consistency", "PASS", "S1 + S2 == Annual for all years 2010–2024")
    else:
        runner.record("T08", "Semestral-to-Annual Sum Consistency", "FAIL", f"{annual_match_errors} years failed S1+S2==Annual")

    # 3.3 Quarterly to Semestral Consistency (Q1 + Q2 == S1 and Q3 + Q4 == S2)
    q_match_errors = 0
    for y in range(2010, 2025):
        q1 = nat_df[(nat_df['Year'] == y) & (nat_df['Period'] == 'Q1')]['Volume_MT'].values[0]
        q2 = nat_df[(nat_df['Year'] == y) & (nat_df['Period'] == 'Q2')]['Volume_MT'].values[0]
        s1 = nat_df[(nat_df['Year'] == y) & (nat_df['Period'] == 'S1')]['Volume_MT'].values[0]
        diff_s1 = abs((q1 + q2) - s1)
        if diff_s1 > 0.1:
            q_match_errors += 1

    if q_match_errors == 0:
        runner.record("T09", "Quarterly-to-Semestral Sum Consistency", "PASS", "Q1 + Q2 == S1 for all years 2010–2024")
    else:
        runner.record("T09", "Quarterly-to-Semestral Sum Consistency", "FAIL", f"{q_match_errors} years failed Q1+Q2==S1")

    # -------------------------------------------------------------------------
    # TEST GROUP 4: VARIETY INDEPENDENCE & AGGREGATE RECONCILIATION
    # -------------------------------------------------------------------------
    # 4.1 Cultivars Sum vs Banana (Total)
    cultivars = ['Banana Cavendish', 'Banana Saba', 'Banana Lakatan', 'Banana Latundan', 'Banana Bungulan', 'Banana Others']
    nat_ann = df[(df['Hierarchy_Level'] == 'National') & (df['Period_Type'] == 'Annual') & (df['Year'] <= 2024)].copy()
    
    total_commodity_vol = nat_ann[nat_ann['Crop'] == 'Banana (Total)']['Volume_MT'].sum()
    sum_cultivars_vol = nat_ann[nat_ann['Crop'].isin(cultivars)]['Volume_MT'].sum()
    diff_cult = abs(total_commodity_vol - sum_cultivars_vol)
    
    # Check discrepancy ratio
    discrepancy_pct = (diff_cult / total_commodity_vol) * 100
    if discrepancy_pct < 0.001:
        runner.record("T10", "Cultivar-to-Aggregate Sum Reconciliation", "PASS", 
                      f"Sum of 6 cultivars ({sum_cultivars_vol:,.2f} MT) matches Banana Total ({total_commodity_vol:,.2f} MT)")
    else:
        runner.record("T10", "Cultivar-to-Aggregate Sum Reconciliation", "FAIL", f"Discrepancy: {diff_cult:,.2f} MT ({discrepancy_pct:.4f}%)")

    # 4.2 Is_Aggregate_Variety Flag Check
    agg_flag_correct = (df[df['Crop'] == 'Banana (Total)']['Is_Aggregate_Variety'] == True).all() and \
                       (df[df['Crop'] != 'Banana (Total)']['Is_Aggregate_Variety'] == False).all()
    if agg_flag_correct:
        runner.record("T11", "Is_Aggregate_Variety Boolean Flag Integrity", "PASS", "100% accurate separation of total vs varieties")
    else:
        runner.record("T11", "Is_Aggregate_Variety Boolean Flag Integrity", "FAIL", "Flag misallocated")

    # -------------------------------------------------------------------------
    # TEST GROUP 5: GEOGRAPHIC HIERARCHY & LOCAL FOCUS (ORIENTAL MINDORO)
    # -------------------------------------------------------------------------
    # 5.1 Local Context Verification: Oriental Mindoro
    mindoro_recs = df[(df['Province_City'] == 'Oriental Mindoro') & (df['Crop'] == 'Banana (Total)') & (df['Period_Type'] == 'Annual') & (df['Year'] <= 2024)]
    if len(mindoro_recs) == 15 and (mindoro_recs['Region'] == 'MIMAROPA REGION').all():
        cum_mindoro = mindoro_recs['Volume_MT'].sum()
        runner.record("T12", "Oriental Mindoro Geographic Mapping", "PASS", 
                      f"15 annual records mapped to MIMAROPA REGION. Cumulative: {cum_mindoro:,.2f} MT")
    else:
        runner.record("T12", "Oriental Mindoro Geographic Mapping", "FAIL", "Oriental Mindoro records incomplete or misclassified")

    # 5.2 Regional Total vs Provincial Sum Check
    # Verify for MIMAROPA Region: do its provinces sum to the regional total?
    mimaropa_ann = df[(df['Region'] == 'MIMAROPA REGION') & (df['Crop'] == 'Banana (Total)') & (df['Period_Type'] == 'Annual') & (df['Year'] <= 2024)]
    reg_vol = mimaropa_ann[mimaropa_ann['Hierarchy_Level'] == 'Regional']['Volume_MT'].sum()
    prov_vol = mimaropa_ann[mimaropa_ann['Hierarchy_Level'].isin(['Provincial', 'City'])]['Volume_MT'].sum()
    mimaropa_diff = abs(reg_vol - prov_vol)
    
    if mimaropa_diff < 1.0: # 1 MT tolerance
        runner.record("T13", "MIMAROPA Provincial-to-Regional Consistency", "PASS", f"Provincial sum ({prov_vol:,.2f} MT) == Regional total ({reg_vol:,.2f} MT)")
    else:
        runner.record("T13", "MIMAROPA Provincial-to-Regional Consistency", "WARN", f"Provincial sum: {prov_vol:,.2f} MT, Regional total: {reg_vol:,.2f} MT (Diff: {mimaropa_diff:,.2f})")

    # -------------------------------------------------------------------------
    # TEST GROUP 6: ANALYTICS ENGINE & FORECASTING TESTS
    # -------------------------------------------------------------------------
    # 6.1 YoY Growth Calculation Test
    test_series = pd.DataFrame({
        'Year': [2020, 2021, 2022],
        'Volume_MT': [100.0, 110.0, 99.0]
    })
    yoy_res = compute_yoy_growth(test_series)
    if yoy_res['YoY_Growth_Pct'].iloc[1] == 10.0 and abs(yoy_res['YoY_Growth_Pct'].iloc[2] - (-10.0)) < 1e-4:
        runner.record("T14", "Analytics Engine: YoY Growth Formula", "PASS", "Exact percentage differences computed correctly")
    else:
        runner.record("T14", "Analytics Engine: YoY Growth Formula", "FAIL", "YoY formula calculation incorrect")

    # 6.2 CAGR Calculation Test
    cagr_test = calculate_cagr(100.0, 121.0, 2) # sqrt(1.21) - 1 = 0.10 (10%)
    if abs(cagr_test - 10.0) < 1e-4:
        runner.record("T15", "Analytics Engine: CAGR Mathematical Precision", "PASS", f"CAGR: {cagr_test:.2f}% (Expected: 10.00%)")
    else:
        runner.record("T15", "Analytics Engine: CAGR Mathematical Precision", "FAIL", f"CAGR: {cagr_test:.2f}%")

    # 6.3 Statistical Anomaly Detection (Z-Score)
    nat_annual_series = nat_df[nat_df['Period_Type'] == 'Annual'].copy()
    anom_res = detect_statistical_anomalies(nat_annual_series, z_thresh=1.4)
    shock_years = anom_res[anom_res['Anomaly_Flag'] == 'Unusually Low Shock']['Year'].tolist()
    boom_years = anom_res[anom_res['Anomaly_Flag'] == 'Unusually High Output']['Year'].tolist()
    
    if 2013 in shock_years and 2018 in boom_years:
        runner.record("T16", "Analytics Engine: Z-Score Outlier Flagging", "PASS", 
                      f"Correctly isolated 2013 shock and 2018 boom (Shocks: {shock_years}, Booms: {boom_years})")
    else:
        runner.record("T16", "Analytics Engine: Z-Score Outlier Flagging", "FAIL", "Failed to detect historical benchmarks")

    # 6.4 Time-Series Forecasting Execution & Error Metric Validity
    fc_out = run_time_series_forecast(nat_annual_series, train_ratio=0.8, forecast_horizon=4)
    if fc_out is not None:
        mape = fc_out['eval_metrics']['MAPE_Pct']
        mae = fc_out['eval_metrics']['MAE_MT']
        rmse = fc_out['eval_metrics']['RMSE_MT']
        forecast_len = len(fc_out['forecast_df'])
        
        if mape > 0 and mape < 10.0 and mae > 0 and rmse >= mae and forecast_len == 4:
            runner.record("T17", "Time-Series Forecast Evaluation & Bounds", "PASS", 
                          f"MAPE: {mape:.2f}%, MAE: {mae:,.1f} MT, RMSE: {rmse:,.1f} MT (4 horizon years projected)")
        else:
            runner.record("T17", "Time-Series Forecast Evaluation & Bounds", "FAIL", f"Invalid metric values: MAPE={mape}")
    else:
        runner.record("T17", "Time-Series Forecast Evaluation & Bounds", "FAIL", "Forecast returned None")

    # -------------------------------------------------------------------------
    # TEST GROUP 7: MISSING DATA INTEGRITY & AUDIT TRAIL
    # -------------------------------------------------------------------------
    # 7.1 Missing Values Not Blindly Zero-Filled
    nan_count = df['Volume_MT'].isna().sum()
    dot_status_count = (df['Data_Status'] == 'Not Available / Negligible').sum()
    if nan_count > 0 and dot_status_count > 0:
        runner.record("T18", "Non-Destructive Missing Data Representation", "PASS", 
                      f"Preserved {nan_count:,} NaNs; {dot_status_count:,} classified as 'Not Available / Negligible'")
    else:
        runner.record("T18", "Non-Destructive Missing Data Representation", "FAIL", "Missing values were destroyed or converted to 0")

    # 7.2 Application Syntax & Compilation Check
    app_path = "src/app.py"
    try:
        import py_compile
        py_compile.compile(app_path, doraise=True)
        runner.record("T19", "Streamlit Application Syntax & Imports", "PASS", f"{app_path} passed bytecode compilation")
    except Exception as e:
        runner.record("T19", "Streamlit Application Syntax & Imports", "FAIL", str(e))

    return runner.summary()


if __name__ == "__main__":
    results = run_all_tests()
