"""
src/analytics_engine.py
-----------------------
Advanced Mathematical & Statistical Analytics Engine for BananaScope PH.

Core Capabilities:
1. Year-over-Year (YoY) Growth & Compound Annual Growth Rate (CAGR).
2. Trend Modeling: 3-Year Rolling Moving Average (SMA) & Ordinary Least Squares (OLS) Linear Regression.
3. Statistical Anomaly & Shock Detection (Z-Score & IQR Outlier Analysis).
4. Time-Series Exploratory Forecasting with Train/Test Evaluation (Holt's Linear Smoothing & OLS).
"""

import numpy as np
import pandas as pd


def compute_yoy_growth(df_input: pd.DataFrame, value_col: str = 'Volume_MT') -> pd.DataFrame:
    """
    Calculates absolute and percentage Year-over-Year (YoY) production growth.
    
    Mathematical Formulation:
      Δ Volume (t) = V_t - V_(t-1)
      YoY Growth % (t) = ((V_t - V_(t-1)) / V_(t-1)) * 100
    """
    df = df_input.sort_values('Year').copy()
    df['YoY_Diff_MT'] = df[value_col].diff()
    df['YoY_Growth_Pct'] = (df['YoY_Diff_MT'] / df[value_col].shift(1)) * 100
    return df


def calculate_cagr(start_val: float, end_val: float, num_years: int) -> float:
    """
    Calculates Compound Annual Growth Rate (CAGR).
    
    Formula:
      CAGR = (End_Value / Start_Value) ** (1 / num_years) - 1
    """
    if start_val <= 0 or end_val <= 0 or num_years <= 0:
        return 0.0
    return ((end_val / start_val) ** (1.0 / num_years) - 1.0) * 100.0


def compute_trend_models(df_input: pd.DataFrame, value_col: str = 'Volume_MT', window: int = 3):
    """
    Computes 3-year Simple Moving Average (SMA_3) and Ordinary Least Squares (OLS) Linear Trend.
    
    Formulas:
      SMA_k(t) = (1/k) * sum_{i=0}^{k-1} V_{t-i}
      Linear Trend: y_hat = beta_0 + beta_1 * t
      Slope (beta_1) = Cov(t, y) / Var(t)
      R^2 = 1 - (SS_res / SS_tot)
    """
    df = df_input.sort_values('Year').copy()
    
    # 1. Rolling Moving Average
    df['SMA_3'] = df[value_col].rolling(window=window, min_periods=1).mean()
    
    # 2. OLS Linear Regression
    valid = df.dropna(subset=['Year', value_col])
    if len(valid) >= 3:
        x = valid['Year'].values.astype(float)
        y = valid[value_col].values.astype(float)
        
        # Fit polynomial deg 1
        slope, intercept = np.polyfit(x, y, 1)
        y_pred = slope * x + intercept
        
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        
        df['Linear_Trend'] = slope * df['Year'].values + intercept
        trend_stats = {
            'slope_mt_per_year': slope,
            'intercept': intercept,
            'r_squared': r_squared,
            'direction': 'Increasing' if slope > 0 else 'Decreasing'
        }
    else:
        df['Linear_Trend'] = np.nan
        trend_stats = {
            'slope_mt_per_year': 0.0,
            'intercept': 0.0,
            'r_squared': 0.0,
            'direction': 'Insufficient Data'
        }
        
    return df, trend_stats


def detect_statistical_anomalies(df_input: pd.DataFrame, value_col: str = 'Volume_MT', z_thresh: float = 1.5):
    """
    Identifies unusually high or low production values using Z-score and Interquartile Range (IQR).
    
    Formulas:
      Z-Score: Z_t = (V_t - mu) / sigma
      IQR Method: IQR = Q_3 - Q_1
        Lower Bound = Q_1 - 1.5 * IQR
        Upper Bound = Q_3 + 1.5 * IQR
    """
    df = df_input.sort_values('Year').copy()
    vals = df[value_col].dropna()
    
    if len(vals) < 4:
        df['Z_Score'] = 0.0
        df['Anomaly_Flag'] = 'Normal'
        return df
        
    mean = vals.mean()
    std = vals.std(ddof=1)
    q1 = vals.quantile(0.25)
    q3 = vals.quantile(0.75)
    iqr = q3 - q1
    iqr_lower = q1 - 1.5 * iqr
    iqr_upper = q3 + 1.5 * iqr
    
    df['Z_Score'] = (df[value_col] - mean) / std if std > 0 else 0.0
    
    flags = []
    for val, z in zip(df[value_col], df['Z_Score']):
        if pd.isna(val):
            flags.append('Unrecorded')
        elif z > z_thresh or val > iqr_upper:
            flags.append('Unusually High Output')
        elif z < -z_thresh or val < iqr_lower:
            flags.append('Unusually Low Shock')
        else:
            flags.append('Normal Production')
            
    df['Anomaly_Flag'] = flags
    return df


def holt_linear_smoothing(train_series: np.ndarray, horizon: int, alpha: float = 0.5, beta: float = 0.3):
    """
    Double Exponential Smoothing (Holt's Linear Trend Method).
    
    Formulas:
      Level: ell_t = alpha * y_t + (1 - alpha) * (ell_{t-1} + b_{t-1})
      Trend: b_t = beta * (ell_t - ell_{t-1}) + (1 - beta) * b_{t-1}
      h-step Forecast: y_hat_{t+h} = ell_t + h * b_t
    """
    n = len(train_series)
    levels = np.zeros(n)
    trends = np.zeros(n)
    
    # Initialize level and trend
    levels[0] = train_series[0]
    trends[0] = train_series[1] - train_series[0] if n > 1 else 0.0
    
    # Forward recursion
    for t in range(1, n):
        levels[t] = alpha * train_series[t] + (1 - alpha) * (levels[t - 1] + trends[t - 1])
        trends[t] = beta * (levels[t] - levels[t - 1]) + (1 - beta) * trends[t - 1]
        
    # In-sample fitted values
    fitted = np.zeros(n)
    fitted[0] = train_series[0]
    for t in range(1, n):
        fitted[t] = levels[t - 1] + trends[t - 1]
        
    # Out-of-sample forecast
    forecasts = np.zeros(horizon)
    last_level = levels[-1]
    last_trend = trends[-1]
    for h in range(1, horizon + 1):
        forecasts[h - 1] = last_level + h * last_trend
        
    return fitted, forecasts


def run_time_series_forecast(
    df_input: pd.DataFrame,
    value_col: str = 'Volume_MT',
    train_ratio: float = 0.8,
    forecast_horizon: int = 4
):
    """
    Performs exploratory time-series forecasting with rigorous Train/Test split and error evaluation.
    
    Process:
      1. Slices validated historical data (2010–2024).
      2. Splits into Training Set (80%) and Testing Set (20%).
      3. Trains Holt's Linear Exponential Smoothing on Training data.
      4. Evaluates accuracy against actual Test data using MAE, RMSE, MAPE.
      5. Retrains on complete historical series to project exploratory forecasts for 2025–2028.
    """
    df = df_input.sort_values('Year').dropna(subset=['Year', value_col]).copy()
    
    # Use only certified historical data (<= 2024)
    hist_df = df[df['Year'] <= 2024].copy()
    
    if len(hist_df) < 5:
        return None  # Insufficient data points for train/test split
        
    years = hist_df['Year'].values
    actuals = hist_df[value_col].values
    
    # 1. Train / Test Split
    split_idx = int(len(hist_df) * train_ratio)
    split_idx = max(split_idx, len(hist_df) - 3) # Ensure at least 2-3 test points
    
    train_years = years[:split_idx]
    train_vals = actuals[:split_idx]
    test_years = years[split_idx:]
    test_vals = actuals[split_idx:]
    
    # 2. Fit on Train set to test prediction accuracy
    test_horizon = len(test_vals)
    _, test_preds = holt_linear_smoothing(train_vals, horizon=test_horizon, alpha=0.6, beta=0.2)
    
    # 3. Calculate Error Evaluation Metrics
    test_errors = test_vals - test_preds
    mae = float(np.mean(np.abs(test_errors)))
    rmse = float(np.sqrt(np.mean(test_errors ** 2)))
    # Mean Absolute Percentage Error (MAPE)
    mape = float(np.mean(np.abs(test_errors / test_vals))) * 100.0
    
    # 4. Out-of-Sample Forecasting (Full series retraining)
    last_hist_year = int(years[-1])
    future_years = np.array([last_hist_year + i for i in range(1, forecast_horizon + 1)])
    
    fitted_full, future_forecasts = holt_linear_smoothing(actuals, horizon=forecast_horizon, alpha=0.6, beta=0.2)
    
    # Construct 95% Confidence Interval band: +/- 1.96 * RMSE
    ci_margin = 1.96 * rmse
    lower_bound = np.maximum(future_forecasts - ci_margin, 0.0) # non-negative
    upper_bound = future_forecasts + ci_margin
    
    # Pack result dataframes
    train_df = pd.DataFrame({'Year': train_years, 'Volume_MT': train_vals, 'Type': 'Historical (Training)'})
    test_df = pd.DataFrame({'Year': test_years, 'Volume_MT': test_vals, 'Predicted_MT': test_preds, 'Type': 'Historical (Test Evaluation)'})
    
    forecast_df = pd.DataFrame({
        'Year': future_years,
        'Projected_MT': future_forecasts,
        'Lower_CI_MT': lower_bound,
        'Upper_CI_MT': upper_bound,
        'Type': 'Exploratory Estimate (Forecast)'
    })
    
    eval_metrics = {
        'MAE_MT': mae,
        'RMSE_MT': rmse,
        'MAPE_Pct': mape,
        'Train_Years': f"{train_years[0]}–{train_years[-1]} ({len(train_years)} years)",
        'Test_Years': f"{test_years[0]}–{test_years[-1]} ({len(test_years)} years)",
        'Method': "Holt's Linear Trend Exponential Smoothing (α=0.6, β=0.2)"
    }
    
    return {
        'train_df': train_df,
        'test_df': test_df,
        'forecast_df': forecast_df,
        'eval_metrics': eval_metrics,
        'fitted_full': fitted_full
    }


if __name__ == "__main__":
    # Test script with national data
    raw_df = pd.read_csv("outputs/cleaned_banana_data.csv")
    nat = raw_df[(raw_df['Hierarchy_Level'] == 'National') & 
                 (raw_df['Crop'] == 'Banana (Total)') & 
                 (raw_df['Period_Type'] == 'Annual')].copy()
                 
    yoy_df = compute_yoy_growth(nat)
    trend_df, t_stats = compute_trend_models(nat)
    anom_df = detect_statistical_anomalies(nat)
    fc_results = run_time_series_forecast(nat)
    
    print("=== YoY Growth Sample ===")
    print(yoy_df[['Year', 'Volume_MT', 'YoY_Diff_MT', 'YoY_Growth_Pct']].tail())
    print("\n=== Trend Stats ===")
    print(t_stats)
    print("\n=== Anomalies Detected ===")
    print(anom_df[anom_df['Anomaly_Flag'] != 'Normal Production'][['Year', 'Volume_MT', 'Z_Score', 'Anomaly_Flag']])
    print("\n=== Forecast Accuracy Metrics ===")
    print(fc_results['eval_metrics'])
    print("\n=== Future Exploratory Estimates ===")
    print(fc_results['forecast_df'])
