"""
src/eda_analysis.py
-------------------
Exploratory Data Analysis (EDA) Engine for BananaScope PH.
Calculates statistical summaries and generates academic visualizations
using Matplotlib and Plotly Express.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import plotly.express as px

# Configure academic visual style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.labelweight'] = 'bold'

INPUT_CSV = "outputs/cleaned_banana_data.csv"
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_data():
    """Loads cleaned tidy dataset."""
    df = pd.read_csv(INPUT_CSV)
    return df


def analyze_annual_production(df):
    """
    1. Total annual banana production.
    2. Average annual production.
    3. Highest and lowest production years.
    4. Year-over-year production differences and growth rates.
    Units: Metric Tons (MT).
    """
    print("\n--- 1. NATIONAL ANNUAL PRODUCTION TRENDS (2010–2024) ---")
    
    # Filter for National Aggregate Annual records
    nat_annual = df[
        (df['Hierarchy_Level'] == 'National') & 
        (df['Crop'] == 'Banana (Total)') & 
        (df['Period_Type'] == 'Annual') &
        (df['Year'] <= 2024) & # Validated historical period
        (df['Volume_MT'].notna())
    ].sort_values('Year').copy()

    # Calculations
    nat_annual['YoY_Diff_MT'] = nat_annual['Volume_MT'].diff()
    nat_annual['YoY_Growth_Pct'] = (nat_annual['YoY_Diff_MT'] / nat_annual['Volume_MT'].shift(1)) * 100

    total_prod = nat_annual['Volume_MT'].sum()
    mean_prod = nat_annual['Volume_MT'].mean()
    std_prod = nat_annual['Volume_MT'].std()
    
    max_row = nat_annual.loc[nat_annual['Volume_MT'].idxmax()]
    min_row = nat_annual.loc[nat_annual['Volume_MT'].idxmin()]

    print(f"Total Cumulative Production (2010–2024) : {total_prod:,.2f} MT")
    print(f"Average Annual Production               : {mean_prod:,.2f} MT (Std: {std_prod:,.2f})")
    print(f"Peak Production Year                    : {int(max_row['Year'])} ({max_row['Volume_MT']:,.2f} MT)")
    print(f"Lowest Production Year                  : {int(min_row['Year'])} ({min_row['Volume_MT']:,.2f} MT)")
    print(f"Absolute Range (Peak - Lowest)          : {max_row['Volume_MT'] - min_row['Volume_MT']:,.2f} MT")

    # Save summary table
    summary_cols = ['Year', 'Volume_MT', 'YoY_Diff_MT', 'YoY_Growth_Pct']
    nat_annual[summary_cols].to_csv(os.path.join(OUTPUT_DIR, "eda_annual_trends.csv"), index=False)

    # Visualization: Figure 1
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    ax.plot(nat_annual['Year'], nat_annual['Volume_MT'] / 1e6, marker='o', color='#1f77b4', linewidth=2.5, markersize=7)
    ax.fill_between(nat_annual['Year'], nat_annual['Volume_MT'] / 1e6, color='#1f77b4', alpha=0.15)
    
    # Annotations
    ax.axhline(mean_prod / 1e6, color='red', linestyle='--', linewidth=1.2, label=f"15-Year Mean: {mean_prod/1e6:.2f}M MT")
    
    # Annotate peak and trough
    ax.annotate(f"Peak (2018): {max_row['Volume_MT']/1e6:.2f}M MT", 
                xy=(max_row['Year'], max_row['Volume_MT'] / 1e6),
                xytext=(max_row['Year'] - 2.5, (max_row['Volume_MT'] / 1e6) + 0.15),
                arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.2),
                fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffffcc', edgecolor='#cccc00'))

    ax.annotate(f"Trough (2024): {min_row['Volume_MT']/1e6:.2f}M MT\n(-8.0% from 2018)", 
                xy=(min_row['Year'], min_row['Volume_MT'] / 1e6),
                xytext=(min_row['Year'] - 3.8, (min_row['Volume_MT'] / 1e6) - 0.25),
                arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.2),
                fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffcccc', edgecolor='#cc0000'))

    ax.set_title("Figure 1: National Annual Banana Production Trajectory in the Philippines (2010–2024)", pad=15)
    ax.set_xlabel("Calendar Year")
    ax.set_ylabel("Volume of Production (Million Metric Tons)")
    ax.set_xticks(nat_annual['Year'])
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2fM'))
    ax.legend(loc='lower left')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig1_annual_production_trend.png"))
    plt.close()

    return nat_annual


def analyze_quarterly_patterns(df):
    """
    5. Quarterly production patterns (seasonality).
    Units: Metric Tons (MT).
    """
    print("\n--- 2. QUARTERLY SEASONALITY PATTERNS (2010–2024) ---")
    
    nat_q = df[
        (df['Hierarchy_Level'] == 'National') & 
        (df['Crop'] == 'Banana (Total)') & 
        (df['Period_Type'] == 'Quarterly') &
        (df['Year'] <= 2024) &
        (df['Volume_MT'].notna())
    ].copy()

    q_summary = nat_q.groupby('Period')['Volume_MT'].agg(
        Total_Volume_MT='sum',
        Mean_Volume_MT='mean',
        Std_Volume_MT='std',
        Min_Volume_MT='min',
        Max_Volume_MT='max'
    ).reindex(['Q1', 'Q2', 'Q3', 'Q4'])

    total_quarterly_volume = q_summary['Total_Volume_MT'].sum()
    q_summary['Share_Pct'] = (q_summary['Total_Volume_MT'] / total_quarterly_volume) * 100

    print(q_summary[['Mean_Volume_MT', 'Share_Pct', 'Min_Volume_MT', 'Max_Volume_MT']])
    q_summary.to_csv(os.path.join(OUTPUT_DIR, "eda_quarterly_seasonality.csv"))

    # Visualization: Figure 2
    quarters = ['Q1 (Jan–Mar)', 'Q2 (Apr–Jun)', 'Q3 (Jul–Sep)', 'Q4 (Oct–Dec)']
    means = q_summary['Mean_Volume_MT'] / 1e6
    colors = ['#aec7e8', '#2ca02c', '#ff7f0e', '#1f77b4']

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    bars = ax.bar(quarters, means, color=colors, edgecolor='black', width=0.55, linewidth=1)
    
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.02, f"{h:.3f}M MT\n({(h/means.sum())*100:.1f}%)", 
                ha='center', va='bottom', fontweight='bold', fontsize=10)

    ax.set_ylim(0, max(means) * 1.22)
    ax.set_title("Figure 2: Average Intra-Annual Quarterly Banana Harvest Distribution (2010–2024)", pad=15)
    ax.set_xlabel("Reporting Quarter (Calendar Period)")
    ax.set_ylabel("Average Quarterly Volume (Million Metric Tons)")
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2fM'))
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig2_quarterly_seasonality.png"))
    plt.close()

    return q_summary


def analyze_regional_rankings(df):
    """
    6. Regional production totals, shares, and rankings.
    Units: Metric Tons (MT).
    """
    print("\n--- 3. REGIONAL PRODUCTION RANKINGS (2010–2024) ---")
    
    reg_annual = df[
        (df['Hierarchy_Level'] == 'Regional') & 
        (df['Crop'] == 'Banana (Total)') & 
        (df['Period_Type'] == 'Annual') &
        (df['Year'] <= 2024) &
        (df['Volume_MT'].notna())
    ].copy()

    reg_summary = reg_annual.groupby('Region')['Volume_MT'].agg(
        Cumulative_Volume_MT='sum',
        Annual_Average_MT='mean',
        Min_Annual_MT='min',
        Max_Annual_MT='max'
    ).reset_index()

    total_reg_vol = reg_summary['Cumulative_Volume_MT'].sum()
    reg_summary['National_Share_Pct'] = (reg_summary['Cumulative_Volume_MT'] / total_reg_vol) * 100
    reg_summary.sort_values(by='Cumulative_Volume_MT', ascending=False, inplace=True)
    reg_summary['Rank'] = range(1, len(reg_summary) + 1)

    print(reg_summary[['Rank', 'Region', 'Cumulative_Volume_MT', 'Annual_Average_MT', 'National_Share_Pct']].to_string(index=False))
    reg_summary.to_csv(os.path.join(OUTPUT_DIR, "eda_regional_rankings.csv"), index=False)

    # Visualization: Figure 3 (Horizontal Bar Chart)
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    plot_data = reg_summary.sort_values('Cumulative_Volume_MT', ascending=True)
    
    # Highlight Davao, Northern Mindanao, and MIMAROPA
    bar_colors = []
    for r in plot_data['Region']:
        if 'DAVAO' in r:
            bar_colors.append('#1f77b4') # Blue
        elif 'MIMAROPA' in r:
            bar_colors.append('#2ca02c') # Green (Local Context)
        elif 'NORTHERN MINDANAO' in r:
            bar_colors.append('#ff7f0e') # Orange
        else:
            bar_colors.append('#c7c7c7') # Gray

    bars = ax.barh(plot_data['Region'], plot_data['Cumulative_Volume_MT'] / 1e6, color=bar_colors, edgecolor='black', height=0.65)
    
    for bar in bars:
        w = bar.get_width()
        pct = (w / (total_reg_vol / 1e6)) * 100
        ax.text(w + 0.8, bar.get_y() + bar.get_height() / 2, f"{w:.2f}M MT ({pct:.1f}%)", 
                va='center', ha='left', fontsize=9.5, fontweight='bold' if w > 5 else 'normal')

    ax.set_xlim(0, max(plot_data['Cumulative_Volume_MT'] / 1e6) * 1.25)
    ax.set_title("Figure 3: Cumulative Regional Banana Production Rankings in the Philippines (2010–2024)", pad=15)
    ax.set_xlabel("Cumulative Production Volume (Million Metric Tons)")
    ax.set_ylabel("Administrative Region")
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0fM'))
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig3_regional_rankings.png"))
    plt.close()

    return reg_summary


def analyze_provincial_rankings(df):
    """
    7. Provincial production rankings (Top 10 national and Oriental Mindoro focus).
    Units: Metric Tons (MT).
    """
    print("\n--- 4. PROVINCIAL PRODUCTION RANKINGS (2010–2024) ---")
    
    prov_annual = df[
        (df['Hierarchy_Level'].isin(['Provincial', 'City'])) & 
        (df['Crop'] == 'Banana (Total)') & 
        (df['Period_Type'] == 'Annual') &
        (df['Year'] <= 2024) &
        (df['Volume_MT'].notna())
    ].copy()

    prov_summary = prov_annual.groupby(['Province_City', 'Region'])['Volume_MT'].agg(
        Cumulative_Volume_MT='sum',
        Annual_Average_MT='mean'
    ).reset_index()

    total_prov_vol = prov_summary['Cumulative_Volume_MT'].sum()
    prov_summary['National_Share_Pct'] = (prov_summary['Cumulative_Volume_MT'] / total_prov_vol) * 100
    prov_summary.sort_values(by='Cumulative_Volume_MT', ascending=False, inplace=True)
    prov_summary['National_Rank'] = range(1, len(prov_summary) + 1)

    top_10 = prov_summary.head(10)
    print("Top 10 Banana-Producing Provinces:")
    print(top_10[['National_Rank', 'Province_City', 'Region', 'Cumulative_Volume_MT', 'National_Share_Pct']].to_string(index=False))

    # Oriental Mindoro Local Profile
    mindoro_row = prov_summary[prov_summary['Province_City'] == 'Oriental Mindoro']
    if not mindoro_row.empty:
        m_rank = int(mindoro_row['National_Rank'].iloc[0])
        m_cum = float(mindoro_row['Cumulative_Volume_MT'].iloc[0])
        m_share = float(mindoro_row['National_Share_Pct'].iloc[0])
        m_avg = float(mindoro_row['Annual_Average_MT'].iloc[0])
        print(f"\nLocal Profile: Oriental Mindoro")
        print(f"  National Rank           : #{m_rank} out of {len(prov_summary)} provinces/cities")
        print(f"  Cumulative Volume (MT)  : {m_cum:,.2f} MT ({m_share:.2f}% of national total)")
        print(f"  Annual Average (MT)     : {m_avg:,.2f} MT/year")

    prov_summary.to_csv(os.path.join(OUTPUT_DIR, "eda_top_provinces.csv"), index=False)

    # Visualization: Figure 4 (Top 10 + Oriental Mindoro)
    display_df = pd.concat([top_10, mindoro_row]).drop_duplicates(subset=['Province_City']).sort_values('Cumulative_Volume_MT', ascending=True)

    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=300)
    bar_colors = ['#2ca02c' if 'Mindoro' in p else '#1f77b4' for p in display_df['Province_City']]
    
    bars = ax.barh(display_df['Province_City'], display_df['Cumulative_Volume_MT'] / 1e6, color=bar_colors, edgecolor='black', height=0.6)
    
    for bar in bars:
        w = bar.get_width()
        pct = (w / (total_prov_vol / 1e6)) * 100
        ax.text(w + 0.3, bar.get_y() + bar.get_height() / 2, f"{w:.2f}M MT ({pct:.1f}%)", 
                va='center', ha='left', fontsize=9.5, fontweight='bold')

    ax.set_xlim(0, max(display_df['Cumulative_Volume_MT'] / 1e6) * 1.2)
    ax.set_title("Figure 4: Top Commercial Banana Provinces in the Philippines vs. Oriental Mindoro (2010–2024)", pad=15)
    ax.set_xlabel("Cumulative Production Volume (Million Metric Tons)")
    ax.set_ylabel("Province / City")
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.1fM'))
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig4_top_provinces.png"))
    plt.close()

    return prov_summary


def analyze_banana_varieties(df):
    """
    8. Differences among banana varieties (Cavendish, Saba, Lakatan, Latundan, Bungulan, Others).
    Units: Metric Tons (MT).
    """
    print("\n--- 5. BANANA VARIETY BREAKDOWN & CULTIVAR COMPARISON (2010–2024) ---")
    
    # Filter for national-level specific cultivars (exclude 'Banana (Total)' aggregate)
    var_annual = df[
        (df['Hierarchy_Level'] == 'National') & 
        (df['Crop'] != 'Banana (Total)') & 
        (df['Period_Type'] == 'Annual') &
        (df['Year'] <= 2024) &
        (df['Volume_MT'].notna())
    ].copy()

    var_summary = var_annual.groupby('Crop')['Volume_MT'].agg(
        Cumulative_Volume_MT='sum',
        Annual_Average_MT='mean',
        Min_Annual_MT='min',
        Max_Annual_MT='max'
    ).reset_index()

    total_var_vol = var_summary['Cumulative_Volume_MT'].sum()
    var_summary['National_Share_Pct'] = (var_summary['Cumulative_Volume_MT'] / total_var_vol) * 100
    var_summary.sort_values(by='Cumulative_Volume_MT', ascending=False, inplace=True)
    var_summary['Rank'] = range(1, len(var_summary) + 1)

    print(var_summary[['Rank', 'Crop', 'Cumulative_Volume_MT', 'Annual_Average_MT', 'National_Share_Pct']].to_string(index=False))
    var_summary.to_csv(os.path.join(OUTPUT_DIR, "eda_variety_summary.csv"), index=False)

    # Visualization: Figure 5 (Variety Share Donut Chart)
    fig, ax = plt.subplots(figsize=(8, 6.5), dpi=300)
    palette = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd', '#8c564b']
    
    wedges, texts, autotexts = ax.pie(
        var_summary['Cumulative_Volume_MT'],
        labels=var_summary['Crop'].str.replace('Banana ', ''),
        autopct='%1.1f%%',
        startangle=140,
        colors=palette,
        pctdistance=0.78,
        wedgeprops=dict(width=0.45, edgecolor='black', linewidth=1)
    )
    plt.setp(autotexts, size=10, weight="bold")
    plt.setp(texts, size=11)
    ax.set_title("Figure 5: Philippine Banana Cultivar Market Composition by Volume (2010–2024)", pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig5_variety_distribution.png"))
    plt.close()

    # Visualization: Figure 6 (Multi-Line Variety Trajectory Over Time)
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    for crop_name, group in var_annual.groupby('Crop'):
        clean_label = crop_name.replace('Banana ', '')
        sorted_grp = group.sort_values('Year')
        ax.plot(sorted_grp['Year'], sorted_grp['Volume_MT'] / 1e6, marker='o', label=clean_label, linewidth=2)

    ax.set_title("Figure 6: Annual Production Trajectories by Specific Banana Cultivar (2010–2024)", pad=15)
    ax.set_xlabel("Calendar Year")
    ax.set_ylabel("Annual Volume (Million Metric Tons)")
    ax.set_xticks(range(2010, 2025))
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2fM'))
    ax.legend(title="Cultivar", loc='upper right', frameon=True)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig6_variety_trends_over_time.png"))
    plt.close()

    return var_summary


def analyze_oriental_mindoro_profile(df):
    """
    Dedicated local case study: Oriental Mindoro production history and variety breakdown.
    Units: Metric Tons (MT).
    """
    print("\n--- 6. ORIENTAL MINDORO LOCAL CASE STUDY PROFILE (2010–2024) ---")
    
    m_data = df[
        (df['Province_City'] == 'Oriental Mindoro') & 
        (df['Period_Type'] == 'Annual') &
        (df['Year'] <= 2024) &
        (df['Volume_MT'].notna())
    ].copy()

    m_total = m_data[m_data['Crop'] == 'Banana (Total)'].sort_values('Year')
    m_varieties = m_data[m_data['Crop'] != 'Banana (Total)'].copy()

    m_total.to_csv(os.path.join(OUTPUT_DIR, "eda_oriental_mindoro.csv"), index=False)

    # Visualization: Figure 7 (Oriental Mindoro Historical Volume & Typhoon Impact)
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    bars = ax.bar(m_total['Year'], m_total['Volume_MT'] / 1000, color='#2ca02c', edgecolor='black', width=0.6, alpha=0.85)

    # Highlight typhoon impact years
    # 2016 (Post-Typhoon Nona in Dec 2015)
    # 2020 (Post-Typhoon Tisoy in Dec 2019 / Ursula)
    ax.annotate("Typhoon Nona Impact\n(-55% crash to 57K MT)", 
                xy=(2016, 57.07), xytext=(2013.5, 95),
                arrowprops=dict(facecolor='red', arrowstyle='->', lw=1.2),
                fontweight='bold', color='darkred',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffeeee', edgecolor='red'))

    ax.annotate("Typhoon Tisoy Impact\n(Historic low: 20.5K MT)", 
                xy=(2020, 20.53), xytext=(2018, 5),
                arrowprops=dict(facecolor='red', arrowstyle='->', lw=1.2),
                fontweight='bold', color='darkred',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffeeee', edgecolor='red'))

    ax.set_title("Figure 7: Oriental Mindoro Banana Production Trajectory & Climate Shocks (2010–2024)", pad=15)
    ax.set_xlabel("Calendar Year")
    ax.set_ylabel("Production Volume (Thousand Metric Tons)")
    ax.set_xticks(m_total['Year'])
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0fK MT'))
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig7_mindoro_production_history.png"))
    plt.close()


def main():
    print("=" * 70)
    print(" BANANASCOPE PH: EXPLORATORY DATA ANALYSIS (EDA) ENGINE")
    print("=" * 70)
    
    df = load_data()
    print(f"Loaded cleaned dataset with {len(df):,} total rows.")

    analyze_annual_production(df)
    analyze_quarterly_patterns(df)
    analyze_regional_rankings(df)
    analyze_provincial_rankings(df)
    analyze_banana_varieties(df)
    analyze_oriental_mindoro_profile(df)

    print("\n" + "=" * 70)
    print(" EDA COMPLETED: All statistical summaries and figures saved in outputs/")
    print("=" * 70)


if __name__ == "__main__":
    main()
