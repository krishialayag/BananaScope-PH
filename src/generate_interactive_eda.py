"""
src/generate_interactive_eda.py
-------------------------------
Generates an interactive Plotly HTML report combining the core EDA charts for BananaScope PH.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

df = pd.read_csv("outputs/cleaned_banana_data.csv")
annual_df = pd.read_csv("outputs/eda_annual_trends.csv")
quarterly_df = pd.read_csv("outputs/eda_quarterly_seasonality.csv")
regional_df = pd.read_csv("outputs/eda_regional_rankings.csv")
variety_df = pd.read_csv("outputs/eda_variety_summary.csv")
mindoro_df = pd.read_csv("outputs/eda_oriental_mindoro.csv")

# Create Plotly subplots
fig = make_subplots(
    rows=3, cols=2,
    subplot_titles=(
        "1. National Annual Production (2010–2024)",
        "2. Quarterly Harvest Distribution",
        "3. Top Regional Producers (Million MT)",
        "4. Cultivar Composition (% Volume)",
        "5. Specific Cultivar Trends Over Time",
        "6. Oriental Mindoro Production & Climate Shocks"
    ),
    specs=[
        [{"type": "xy"}, {"type": "xy"}],
        [{"type": "xy"}, {"type": "domain"}],
        [{"type": "xy"}, {"type": "xy"}]
    ],
    vertical_spacing=0.10,
    horizontal_spacing=0.12
)

# 1. National Annual Trend
fig.add_trace(
    go.Scatter(
        x=annual_df['Year'], y=annual_df['Volume_MT'] / 1e6,
        mode='lines+markers', name='National Total',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=7)
    ),
    row=1, col=1
)

# 2. Quarterly Seasonality
quarters = ['Q1 (Jan–Mar)', 'Q2 (Apr–Jun)', 'Q3 (Jul–Sep)', 'Q4 (Oct–Dec)']
q_means = quarterly_df['Mean_Volume_MT'] / 1e6
fig.add_trace(
    go.Bar(
        x=quarters, y=q_means, name='Quarterly Average',
        marker_color=['#aec7e8', '#2ca02c', '#ff7f0e', '#1f77b4'],
        text=[f"{m:.2f}M MT" for m in q_means], textposition='auto'
    ),
    row=1, col=2
)

# 3. Top Regional Producers
top_reg = regional_df.head(8).sort_values('Cumulative_Volume_MT', ascending=True)
fig.add_trace(
    go.Bar(
        x=top_reg['Cumulative_Volume_MT'] / 1e6,
        y=top_reg['Region'].str.replace(r'REGION [IVX]+ \((.*?)\)', r'\1', regex=True),
        orientation='h', name='Regional Volume',
        marker_color='#1f77b4',
        text=[f"{v:.1f}M" for v in top_reg['Cumulative_Volume_MT'] / 1e6], textposition='auto'
    ),
    row=2, col=1
)

# 4. Cultivar Composition (Donut)
fig.add_trace(
    go.Pie(
        labels=variety_df['Crop'].str.replace('Banana ', ''),
        values=variety_df['Cumulative_Volume_MT'],
        hole=0.45, name='Cultivar Share',
        marker=dict(colors=['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd', '#8c564b'])
    ),
    row=2, col=2
)

# 5. Specific Cultivar Trends
var_annual = df[
    (df['Hierarchy_Level'] == 'National') & 
    (df['Crop'] != 'Banana (Total)') & 
    (df['Period_Type'] == 'Annual') & 
    (df['Year'] <= 2024) & 
    (df['Volume_MT'].notna())
]
for crop_name, grp in var_annual.groupby('Crop'):
    sorted_grp = grp.sort_values('Year')
    fig.add_trace(
        go.Scatter(
            x=sorted_grp['Year'], y=sorted_grp['Volume_MT'] / 1e6,
            mode='lines+markers', name=crop_name.replace('Banana ', '')
        ),
        row=3, col=1
    )

# 6. Oriental Mindoro Local Profile
fig.add_trace(
    go.Bar(
        x=mindoro_df['Year'], y=mindoro_df['Volume_MT'] / 1e3,
        name='Oriental Mindoro',
        marker_color='#2ca02c',
        text=[f"{v:.0f}K" for v in mindoro_df['Volume_MT'] / 1e3], textposition='outside'
    ),
    row=3, col=2
)

fig.update_layout(
    title_text="<b>BananaScope PH: Multi-Dimensional Exploratory Data Analysis (EDA)</b>",
    title_x=0.5,
    height=1200,
    width=1350,
    showlegend=False,
    template="plotly_white"
)

output_html = "outputs/interactive_eda_dashboard.html"
fig.write_html(output_html)
print(f"Interactive Plotly dashboard saved to: {output_html}")
