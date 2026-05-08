# 🛡️ Lake Chad Basin Security Dashboard

An interactive conflict intelligence dashboard visualizing armed violence across the Lake Chad Basin region (Nigeria, Niger, Chad, and Cameroon) from 2015 to 2024.

Built with Python and Streamlit using open-source conflict event data from the Uppsala Conflict Data Program (UCDP).

---

## 📸 Features

- **Interactive Conflict Map** — heatmap and clustered marker views with event popups
- **Timeline Analysis** — monthly conflict trends colored by death toll
- **Violence Type Breakdown** — state-based, non-state, and one-sided civilian targeting
- **Most Affected Regions** — state and province level ranking
- **Deadliest Conflicts** — top armed group confrontations by fatalities
- **Filterable Data Table** — drill down into raw event records
- **Sidebar Filters** — filter by country, year range, and violence type

---

## 📊 Data Source

**UCDP Georeferenced Event Dataset (GED) Global v25.1**  
Uppsala Conflict Data Program — Uppsala University, Sweden  
🔗 https://ucdp.uu.se/downloads

> Sundberg, Ralph and Erik Melander (2013) Introducing the UCDP Georeferenced Event Dataset. *Journal of Peace Research* 50(4).

Coverage: 8,019 conflict events across the Lake Chad Basin (2015–2024)  
Total deaths recorded: 54,391 | Civilian deaths: 13,767

---

## 🗺️ Region Coverage

| Country | Events |
|---------|--------|
| Nigeria | 5,232 |
| Cameroon | 2,049 |
| Niger | 575 |
| Chad | 163 |

Key conflict zones: Borno State, Far North Region (Cameroon), Tillabéri Region (Niger), Diffa Region

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/yakubuta/sahel-security-dashboard.git
cd sahel-security-dashboard
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Download the data
- Download **UCDP GED Global v25.1** CSV from https://ucdp.uu.se/downloads
- Place the file in the project root folder
- Run the data pipeline:

```bash
python load_data.py    # filters raw data to Lake Chad Basin
python clean.py        # cleans and processes the data
```

### 4. Launch the dashboard
```bash
python -m streamlit run app.py
```

---

## 📁 Project Structure

```
sahel-security-dashboard/
│
├── app.py              # Main Streamlit dashboard
├── load_data.py        # Filters raw UCDP data to Lake Chad Basin
├── clean.py            # Data cleaning and feature engineering
├── requirements.txt    # Python dependencies
├── README.md
│
└── data/
    ├── raw/
    │   └── ucdp_lake_chad.csv
    └── processed/
        └── ucdp_lake_chad_clean.csv
```

---

## 🔧 Tech Stack

- **Python 3.x**
- **Streamlit** — dashboard UI
- **Folium + streamlit-folium** — interactive maps
- **Plotly** — charts and visualizations
- **Pandas** — data processing

---

## 👤 Author

**Yacub**  
BSc Criminology and Security Studies — Nigerian Army University Biu (NAUB)  
Interests: Conflict analysis, intelligence studies, Sahel security, data-driven security research

---

## ⚠️ Disclaimer

This dashboard is built for academic and research purposes using publicly available open-source data. All conflict data is sourced from UCDP and does not represent any government or institutional position.

---

## 📜 License

MIT License — free to use, modify, and distribute with attribution.
