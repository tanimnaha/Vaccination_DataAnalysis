# Power BI Integration & Dashboard Specification Guide
## Project: Vaccination Data Analysis and Visualization

This guide details the Power BI data architecture, relational Star Schema, DAX measure library, and interactive dashboard layout designs for connecting to the SQLite `vaccination_db.sqlite` database or cleaned CSV files (`data/cleaned/`).

---

## 1. Connecting Power BI to the Data Source

### Method A: Direct SQLite Connector / ODBC (Recommended for Live Relational Sync)
1. Open **Power BI Desktop**.
2. Navigate to `Get Data` -> `More...` -> `Database` -> `ODBC`.
3. Select your installed SQLite DSN or enter the connection string pointing to `database/vaccination_db.sqlite`.
4. Import the following tables and views:
   - `dim_countries`
   - `dim_antigens`
   - `dim_diseases`
   - `fact_coverage`
   - `fact_incidence`
   - `fact_reported_cases`
   - `fact_vaccine_intro`
   - `fact_vaccine_schedule`
   - `fact_socioeconomic`
   - `vw_coverage_incidence_joined`

### Method B: Cleaned CSV Folder Connector
1. Select `Get Data` -> `Folder` -> Select `data/cleaned/`.
2. Click `Transform Data` and combine files into individual queries.

---

## 2. Data Model Architecture (Star Schema)

In Power BI **Model View**, establish the following 1-to-Many ($1 : *$) single-directional relationships:

```
                  +-------------------+
                  |   dim_countries   |
                  +---------+---------+
                            |
        +-------------------+-------------------+-------------------+
        | (1:*)             | (1:*)             | (1:*)             | (1:*)
+-------v-------+   +-------v-------+   +-------v-------+   +-------v-------+
| fact_coverage |   |fact_incidence |   |  fact_cases   |   |fact_socioecon |
+-------^-------+   +-------^-------+   +-------^-------+   +---------------+
        |                   |                   |
        | (1:*)             +---------+---------+
+-------+-------+                     | (1:*)
|  dim_antigens |             +-------v-------+
+---------------+             |  dim_diseases |
                              +---------------+
```

---

## 3. DAX Measure Library

Create a dedicated DAX measures table `_Measures` in Power BI and paste the following formulas:

```dax
// 1. Average Vaccination Coverage %
Average Coverage % = 
AVERAGE(fact_coverage[coverage_pct])

// 2. Total Doses Administered
Total Doses Administered = 
SUM(fact_coverage[doses_administered])

// 3. Total Target Population
Total Target Population = 
SUM(fact_coverage[target_number])

// 4. Global Target Population Coverage %
Global Target Coverage % = 
DIVIDE([Total Doses Administered], [Total Target Population], 0) * 100

// 5. MCV1 to MCV2 Dropout Rate %
MCV Dropout Rate % = 
VAR MCV1_Cov = CALCULATE([Average Coverage %], fact_coverage[antigen_code] = "MCV1")
VAR MCV2_Cov = CALCULATE([Average Coverage %], fact_coverage[antigen_code] = "MCV2")
RETURN
DIVIDE(MCV1_Cov - MCV2_Cov, MCV1_Cov, 0) * 100

// 6. Average Disease Incidence Rate
Average Incidence Rate = 
AVERAGE(fact_incidence[incidence_rate])

// 7. Total Reported Cases
Total Reported Cases = 
SUM(fact_reported_cases[reported_cases])

// 8. Disease Case Reduction % (Historical Peak vs Recent)
Disease Case Reduction % = 
VAR MaxCases = MAXX(ALLSELECTED(fact_reported_cases[year]), [Total Reported Cases])
VAR CurrentCases = [Total Reported Cases]
RETURN
DIVIDE(MaxCases - CurrentCases, MaxCases, 0) * 100

// 9. Urban vs Rural Coverage Disparity Gap
Urban-Rural Coverage Gap % = 
VAR UrbanCov = CALCULATE([Average Coverage %], fact_socioeconomic[subgroup] = "Urban")
VAR RuralCov = CALCULATE([Average Coverage %], fact_socioeconomic[subgroup] = "Rural")
RETURN
UrbanCov - RuralCov

// 10. Outbreak Risk Status Indicator
Outbreak Risk Status = 
IF([Total Reported Cases] > 1.5 * CALCULATE([Total Reported Cases], DATEADD(dim_countries[country_code], -1, YEAR)),
   "HIGH OUTBREAK RISK",
   "NORMAL"
)
```

---

## 4. Interactive Dashboard Layout Specifications

### Page 1: Executive Global Overview Dashboard
- **Header Banner**: Title, WHO Region Slicer, Year Range Slider (2010-2024), Antigen Slicer.
- **Top KPI Cards**:
  1. `Average Coverage %` (Goal: 85%)
  2. `Total Doses Administered` (Formatted in Millions/Billions)
  3. `Total Reported Cases`
  4. `MCV Dropout Rate %`
- **Central Visual**: **Geographical Filled Map** mapping `dim_countries[country_name]` colored by `Average Coverage %` (Green = $\ge 85\%$, Yellow = $70-84\%$, Red = $<70\%$).
- **Bottom Left**: **Dual-Axis Trend Line Chart** showing `Average Coverage %` (Left Y-Axis) vs. `Average Incidence Rate` (Right Y-Axis) across `year`.
- **Bottom Right**: **Clustered Bar Chart** comparing `Average Coverage %` by `dim_countries[who_region]`.

### Page 2: Disease Control & Outbreak Tracker
- **Top Visual**: **Interactive Scatter Plot** plotting `Average Coverage %` (X-Axis) vs. `Average Incidence Rate` (Y-Axis) grouped by `dim_diseases[disease_description]` with a regression trendline.
- **Middle Left**: **Horizontal Bar Chart** showing `Disease Case Reduction %` ranked by disease type.
- **Middle Right**: **Matrix Table** displaying `who_region`, `disease_code`, `Total Reported Cases`, and `Outbreak Risk Status`.
- **Bottom**: **Pre/Post Vaccine Introduction Comparison Bar Chart** comparing case loads before vs. after full vaccine rollout ('No' vs 'Partial' vs 'Yes').

### Page 3: Demographic & Equity Analytics
- **Top Left**: **Urban vs Rural Coverage Comparison** (Clustered Column Chart broken down by `income_group`).
- **Top Right**: **Caregiver Education Impact** (Bar Chart showing Coverage by `Education_Level`: Primary, Secondary, Tertiary).
- **Bottom Left**: **Delivery Strategy Effectiveness** (Grouped Bar Chart comparing `Door-to-Door`, `Centralized Health Clinic`, `Mobile Outreach Unit` on Coverage and Dropout Rates).
- **Bottom Right**: **Gender Parity Gauge Visual** displaying Female vs Male immunization completion rates.

### Page 4: Resource Allocation & Demand Forecasting
- **Top Left**: **Resource Allocation Priority Table** highlighting countries with $<68\%$ coverage tagged as `High Priority Resource Intervention`.
- **Top Right**: **Upcoming Vaccine Demand Forecast Table** projecting next year's dose requirements based on population growth.
- **Bottom**: **Dose Dropout Waterfall Chart** demonstrating step-down losses from 1st dose (MCV1/DTP1) to booster rounds (MCV2/DTP3/HPV).

---

## 5. Scheduled Refresh & Security Settings

1. **Scheduled Refresh**: In Power BI Service, configure scheduled daily refresh at 02:00 UTC under Dataset Settings.
2. **Row-Level Security (RLS)**:
   - Create Role `Region_AFRO`: Filter `dim_countries[who_region] = "AFRO"`
   - Create Role `Region_SEARO`: Filter `dim_countries[who_region] = "SEARO"`
   - Create Role `Region_EURO`: Filter `dim_countries[who_region] = "EURO"`
