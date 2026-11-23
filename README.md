# BananaScope PH: Regional Banana Production Surveillance & Analytics (2010–2026)

## Project Overview
**BananaScope PH** is an automated data analytics and visualization system developed by Grade 12 students in **Fundamentals of Data Analytics** at Leuteboro National High School (DepEd MIMAROPA, Oriental Mindoro). 

The platform monitors, processes, and visualizes 14+ years of multi-variety banana production statistics in the Philippines to support local agricultural planning, farmer cooperatives, and regional supply chain analytics.

---

## Directory Structure
```text
BananaScope_PH/
│
├── data/              # Raw and processed datasets (BananaData.xlsx)
├── src/               # Python source code (data cleaning pipeline & Streamlit app)
├── outputs/           # Generated analytical artifacts, plots, charts, and clean tables
├── paper/             # Formal research paper, project proposals, and documentation
├── README.md          # Project documentation and setup guide
└── BananaData.xlsx    # Original master dataset archive (unmodified)
```

---

## Dataset Information
- **Source:** Philippine Statistics Authority (PSA) OpenStat
- **Dataset Title:** Fruit Crops: Volume of Production, by Region, Province, Quarter, and Semester (2010–2026)
- **Unit of Measurement:** Metric Tons (MT)
- **Focal Commodity:** Banana (Aggregated Total, Cavendish, Saba, Lakatan, Latundan, Bungulan, and Others)
- **Geographic Granularity:** 101 Philippine Geolocation units (National, 17 Regions, and individual Provinces/Cities)
- **Temporal Granularity:** Quarterly (Q1–Q4), Semestral (S1–S2), and Annual totals from 2010 to 2026

---

## Software & Technology Stack
- **Language & Runtime:** Python 3.12
- **Data Engineering:** Pandas, OpenPyXL
- **Web Dashboard:** Streamlit
- **Data Visualization:** Plotly Express
- **AI Development Co-Pilot:** Google Antigravity

---

## Required Dependencies
To run the analysis pipeline and interactive dashboard, install the required packages:
```bash
pip install pandas openpyxl streamlit plotly
```

---

## Research Questions
1. **Temporal Patterns:** Which calendar quarters and seasons consistently record peak banana production across major varieties?
2. **Geographical & Varietal Disparities:** How does commercial production differ between export-oriented Cavendish hubs in Mindanao and domestic staple hubs (Saba, Lakatan) across Luzon and the Visayas (including MIMAROPA)?
3. **Macro Outbreak & Climate Impact:** How have extreme weather events and agricultural shocks (e.g., Panama disease/Fusarium wilt) affected national and regional volume trajectories between 2010 and 2024?
