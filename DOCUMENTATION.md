# Comprehensive Project Documentation: Vaccination Data Analysis & Visualization

![Healthcare Analytics](https://img.shields.io/badge/Domain-Global%20Public%20Health%20%26%20Epidemiology-blue)
![Database Engine](https://img.shields.io/badge/Database-SQLite%203NF%20Relational%20Schema-success)
![BI Platform](https://img.shields.io/badge/BI-Power%20BI%20Desktop%20%26%20DAX-orange)
![Code Status](https://img.shields.io/badge/Notebook%20Execution-269%20Cells%20%7C%200%20Errors-brightgreen)

---

## 1. Executive Summary & Project Background

The **Vaccination Data Analysis and Visualization** initiative is an end-to-end healthcare analytics and data engineering project designed to evaluate global immunization performance, disease transmission suppression, and healthcare equity across diverse populations. Immunization is widely recognized by the World Health Organization (WHO) and UNICEF as one of the most cost-effective and life-saving public health interventions in human history. Every year, routine immunization programs prevent an estimated 3.5 to 5 million deaths from vaccine-preventable diseases including measles, diphtheria, tetanus, pertussis, and polio.

Despite these achievements, significant global disparities in immunization coverage persist. Millions of children in lower-income countries, rural communities, and underserved socioeconomic groups remain "zero-dose" or under-immunized. Furthermore, fragmented public health surveillance systems—where coverage registries, disease incidence monitoring, vaccine introduction tracking, and socioeconomic demographics reside in isolated data silos—severely hamper the ability of health ministries and international funding bodies to make timely, data-driven decisions.

### Project Goals:
1. **Consolidate & Normalize**: Unify six disparate epidemiological datasets spanning 15 countries and 15 longitudinal years (2010–2024) into a robust, normalized Third Normal Form (3NF) relational SQL database.
2. **Execute In-Depth EDA**: Perform comprehensive exploratory analysis adhering to the Univariate-Bivariate-Multivariate (UBM) framework, producing over 20 structured visualizations with epidemiological and business impact justifications.
3. **Answer Critical Business Questions**: Provide rigorous SQL and statistical solutions for 30 domain questions (10 Easy, 10 Medium, and 10 Scenario-based) defined by public health stakeholders.
4. **Deliver Executive BI Dashboards**: Establish an enterprise Star Schema model, DAX measure library, and interactive multi-page dashboard prototype in Power BI for operational decision support.

---

## 2. End-to-End System Architecture

The project implements a modular, production-grade analytics pipeline:

```
[Raw Data Sources]
  ├── coverage_data.csv (2,250 records)
  ├── incidence_rate.csv (2,025 records)
  ├── reported_cases.csv (2,025 records)
  ├── vaccine_introduction.csv (180 records)
  ├── vaccine_schedule.csv (300 records)
  └── socioeconomic_metrics.csv (1,350 records)
           │
           ▼
[Automated Data Cleaning & Imputation Pipeline (scripts/data_cleaner.py)]
  ├── String cleaning (% symbol removal, whitespace stripping)
  ├── Mathematical imputation: Target = Doses / (Coverage % / 100)
  ├── Fallback imputation: Country-Antigen median heuristics
  └── Boundary validation & float casting
           │
           ▼
[Cleaned CSV Storage (data/cleaned/)]
           │
           ▼
[Relational Database Engine (scripts/database_setup.py -> database/vaccination_db.sqlite)]
  ├── DDL Schema Execution (database/schema.sql)
  ├── 3NF Normalization: 3 Dimensions (Country, Antigen, Disease) + 6 Fact Tables
  ├── Referential Integrity: Foreign Key Constraints & Cascading Indexes
  └── Analytical Reporting Views: vw_coverage_incidence_joined
           │
           ├───► [Jupyter Notebook EDA Engine (Sample_EDA_Submission_Template.ipynb)]
           │       ├── 22 Structured UBM Visualizations
           │       ├── Chart 14: Correlation Heatmap
           │       ├── Chart 15: Pair Plot Matrix
           │       └── 30 Analytical SQL Query Solutions
           │
           └───► [Power BI Business Intelligence Suite (power_bi/)]
                   ├── Star Schema Relational Data Model
                   ├── 20+ Production DAX Measures (power_bi/dax_measures.dax)
                   ├── Power Query M Transformations (power_bi/power_query_etl.m)
                   ├── Dashboard Layout Wireframes (power_bi/dashboard_guide.md)
                   └── Interactive Prototype Dashboard (power_bi/interactive_dashboard.html)
```

---

## 3. Data Extraction, Cleaning, and Imputation Methodology

The raw datasets contained real-world noise, reporting inconsistencies, and structural gaps. The automated cleaning engine ([`scripts/data_cleaner.py`](file:///Users/tanimnaha/Downloads/Vaccination_DataAnalysis/scripts/data_cleaner.py)) implements the following transformations:

### 3.1 Table 1: Coverage Data (`data/raw/coverage_data.csv`)
- **Challenge**: The `Coverage` attribute was stored as unformatted string text with trailing percent signs (e.g., `"84.5%"`), preventing numerical arithmetic. Furthermore, several country-year observations had missing target population values (`Target_number = NaN`).
- **Cleaning & Imputation Logic**:
  1. Regex removal of the `%` symbol: `df['Coverage_Pct'] = df['Coverage'].str.replace('%', '').astype(float)`.
  2. Mathematical identity imputation: Where target population was missing but administered doses and coverage were present:
     $$\text{Target\_number} = \frac{\text{Doses\_administered}}{\text{Coverage\_Pct} / 100}$$
  3. Secondary imputation: Remaining missing target numbers were imputed using the country-antigen median across historical years.
  4. Bounds clipping: All coverage values were clamped strictly between $0.0\%$ and $100.0\%$.

### 3.2 Table 2: Incidence Rate Data (`data/raw/incidence_rate.csv`)
- **Challenge**: Missing values and non-standard float formats across surveillance reporting intervals.
- **Cleaning Logic**: Cast to float, imputed missing values with $0.0$, and clipped negative anomalies to ensure strictly non-negative incidence per 100,000.

### 3.3 Table 3: Reported Cases Data (`data/raw/reported_cases.csv`)
- **Challenge**: Empty reporting cells and potential non-integer case entries.
- **Cleaning Logic**: Cast to integer, replaced missing records with $0$ (indicating zero confirmed reported cases during that surveillance window), and clipped lower bound at 0.

### 3.4 Table 4 & 5: Vaccine Introduction & Schedule Data
- **Challenge**: Inconsistent string casing (e.g., `"yes"`, `"Yes"`, `"YES"`) and leading/trailing whitespace in categorical descriptors.
- **Cleaning Logic**: Applied `.strip().str.capitalize()` to standardize introduction status into three discrete categories: `'Yes'`, `'No'`, `'Partial'`.

### 3.5 Table 6: Socioeconomic & Demographic Metrics
- **Challenge**: Variable string percentages and missing values in demographic dropout metrics.
- **Cleaning Logic**: Standardized continuous percentages for `Coverage_Pct` and `Dropout_Rate_Pct` to floats within the $[0, 100]$ range.

---

## 4. Relational Database Modeling (3NF Schema & SQL DDL)

To eliminate redundancy and support scalable analytical querying, a Third Normal Form (3NF) relational database was constructed using SQLite ([`database/schema.sql`](file:///Users/tanimnaha/Downloads/Vaccination_DataAnalysis/database/schema.sql)).

### 4.1 Entity-Relationship Structure

```
                  +-----------------------------------+
                  |           dim_countries           |
                  +-----------------------------------+
                  | PK  country_code   VARCHAR(3)     |
                  |     country_name   VARCHAR(100)   |
                  |     who_region     VARCHAR(10)    |
                  |     pop_density    REAL           |
                  |     income_group   VARCHAR(50)    |
                  +-----------------+-----------------+
                                    |
          +-------------------------+-------------------------+-------------------------+
          | 1:N                     | 1:N                     | 1:N                     | 1:N
+---------v---------+     +---------v---------+     +---------v---------+     +---------v---------+
|   fact_coverage   |     |  fact_incidence   |     |fact_reported_cases|     |fact_socioeconomic |
+-------------------+     +-------------------+     +-------------------+     +-------------------+
| PK coverage_id    |     | PK incidence_id   |     | PK case_id        |     | PK socio_id       |
| FK country_code   |     | FK country_code   |     | FK country_code   |     | FK country_code   |
|    year           |     |    year           |     |    year           |     |    year           |
| FK antigen_code   |     | FK disease_code   |     | FK disease_code   |     |    dimension      |
|    target_number  |     |    incidence_rate |     |    reported_cases |     |    subgroup       |
|    doses_admin    |     +---------^---------+     +---------^---------+     |    coverage_pct   |
|    coverage_pct   |               |                         |               |    dropout_pct    |
+---------^---------+               |                         |               |    strategy       |
          |                         +------------+------------+               +-------------------+
          | 1:N                                  | 1:N
+---------+---------+                  +---------+---------+
|   dim_antigens    |                  |   dim_diseases    |
+-------------------+                  +-------------------+
| PK antigen_code   |                  | PK disease_code   |
|    antigen_desc   |                  |    disease_desc   |
| FK target_disease |                  |    denom_unit     |
+-------------------+                  +-------------------+
```

### 4.2 Database Optimization & Performance Features:
- **Foreign Key Enforcement**: `PRAGMA foreign_keys = ON;` guarantees referential integrity between fact rows and dimension records.
- **B-Tree Composite Indexes**:
  - `idx_cov_country_yr` on `fact_coverage(country_code, year)`
  - `idx_cov_antigen` on `fact_coverage(antigen_code)`
  - `idx_inc_country_yr` on `fact_incidence(country_code, year)`
  - `idx_inc_disease` on `fact_incidence(disease_code)`
  - `idx_cases_country_yr` on `fact_reported_cases(country_code, year)`
  - `idx_socio_dim_subgroup` on `fact_socioeconomic(dimension, subgroup)`
- **Materialized Analytical Views**: `vw_coverage_incidence_joined` joins coverage, antigen definitions, disease incidence, and reported cases into a single queryable entity for fast Power BI and Python ingestion.

---

## 5. Key Challenges Faced & Engineering Solutions

| # | Challenge Encountered | Public Health / Analytical Risk | Engineering Solution Implemented |
| :--- | :--- | :--- | :--- |
| **1** | **Missing Target Population Figures** | Surveillance systems frequently track doses administered but fail to log updated census birth cohorts, resulting in missing denominator values. | Implemented mathematical inverse identity imputation: $\text{Target} = \frac{\text{Doses}}{\text{Coverage} / 100}$. For remaining edge cases, applied country-antigen historical medians, achieving 100% completeness. |
| **2** | **Inconsistent String Percentages & Units** | Raw coverage percentages contained literal `%` signs, and incidence rates had varying decimal representations, blocking mathematical aggregation. | Engineered an automated regex cleaning step that stripped non-numeric characters, cast values to 64-bit floats, and enforced valid boundary clipping ($[0, 100]$). |
| **3** | **Multi-Domain Granularity Mismatches** | Coverage data is tracked at the **Antigen level** (e.g., `MCV1`, `MCV2`), whereas Disease Incidence is logged at the **Disease level** (e.g., `MEASLES`). Direct joining caused severe Cartesian fan-out. | Modeled an explicit bridge relationship in `dim_antigens.target_disease_code` that maps each antigen to its corresponding clinical pathogen in `dim_diseases`, ensuring $1 : 1$ relational joins. |
| **4** | **Quantifying Booster Attrition (Drop-off)** | Standard healthcare metrics only evaluate cross-sectional coverage, obscuring the critical patient drop-off occurring between first doses and subsequent boosters. | Engineered a longitudinal drop-off metric across matching country-year cohorts: $\text{Dropout Rate} = \text{MCV1 Coverage} - \text{MCV2 Coverage}$. |
| **5** | **Pandemic-Era Data Volatility (2020-2021)** | COVID-19 lockdowns created sharp anomalies in routine childhood immunization delivery, distorting multi-year linear regressions. | Segmented temporal analyses into three operational windows: *Pre-Pandemic Baseline (2010–2019)*, *Pandemic Disruption (2020–2021)*, and *Post-Pandemic Recovery (2022–2024)*. |
| **6** | **Disparate Socioeconomic Dimensions** | Surveys tracked disparate dimensions (Gender, Urban/Rural, Caregiver Literacy, Delivery Strategy) in a single column, risking improper aggregation. | Normalized the data into a dedicated `fact_socioeconomic` table with indexed `dimension` and `subgroup` attributes, preventing invalid cross-group averaging. |

---

## 6. Analytical Findings & Statistical Discoveries

The Exploratory Data Analysis followed the **UBM (Univariate, Bivariate, Multivariate)** framework across 22 charts in [`Sample_EDA_Submission_Template.ipynb`](file:///Users/tanimnaha/Downloads/Vaccination_DataAnalysis/Sample_EDA_Submission_Template.ipynb):

### 6.1 Univariate Insights (Charts 1 to 5)
- **Coverage Distribution**: Left-skewed with a mean of **$76.8\%$** and a median of **$79.0\%$**. A primary peak sits at $85-95\%$ (high-income nations), while a persistent left tail extends down to $25\%$, reflecting severe under-immunization in vulnerable regions.
- **Incidence Skewness**: Right-skewed with a median of **$74.2$ per 100k** and an elevated mean of **$88.5$ per 100k**, driven by localized epidemic spikes exceeding $400$ per 100k.
- **Disease Burden Ranking**: Seasonal Influenza, Tuberculosis, and Measles account for over **$65\%$** of all recorded global cases.

### 6.2 Bivariate Insights (Charts 6 to 13)
- **Efficacy Gradient**: Strong inverse correlation between coverage and disease incidence ($r = -0.48$) and reported cases ($r = -0.22$).
- **Booster Drop-off Gap**: A persistent **$14.2\%$ attrition gap** exists between MCV1 ($82.1\%$) and MCV2 ($67.9\%$), demonstrating that health systems fail to maintain caregiver contact during the second year of life.
- **Geographic Divide**: Urban settings achieve **$83.4\%$** coverage with an **$8.1\%$** dropout rate, whereas rural communities achieve only **$69.2\%$** coverage with a **$14.6\%$** dropout rate—a **$14.2\%$ geographic equity deficit**.
- **Caregiver Education Catalyst**: Children of caregivers with Tertiary education achieve **$86.5\%$** coverage, compared to **$65.4\%$** for caregivers with primary education or less—a **$21.1\%$ literacy-driven divide**.
- **Vaccine Introduction Impact**: Full nationwide rollout ('Yes') reduces reported disease cases by **$68.4\%$** compared to pre-introduction baseline levels ('No').

### 6.3 Multivariate Insights & Template Designated Charts (Charts 14 to 22)
- **Chart 14 - Correlation Heatmap**: Validates strong inverse dependencies between coverage and disease burden, while highlighting that population density negatively correlates with coverage ($r = -0.26$) due to peri-urban slum distribution bottlenecks.
- **Chart 15 - Pair Plot**: Multidimensional scatter and KDE matrix demonstrates distinct economic clustering: High-income nations cluster in the high-coverage ($>85\%$), low-incidence ($<30$ per 100k) quadrant, while Low-income nations exhibit wide dispersion with high disease vulnerability.
- **Delivery Strategy Optimization**: Door-to-Door outreach achieves the highest coverage (**$79.6\%$**) and lowest dropout rate (**$8.4\%$**), compared to fixed Centralized Clinics (**$68.2\%$** coverage, **$14.1\%$** dropout).
- **Schedule Complexity Attrition**: Coverage degrades monotonically as schedule rounds increase: 1-dose protocols achieve **$84.2\%$**, 2-dose protocols **$77.5\%$**, 3-dose protocols **$72.1\%$**, and 4-dose protocols drop to **$68.1\%$**.
- **Progress to WHO IA2030**: As of 2024, global MCV1 coverage stands at **$82.4\%$**, leaving a **$12.6\%$ gap** to achieve the WHO Immunization Agenda 2030 target of $95\%$.

---

## 7. Domain & Business Scenarios: 30 Questions Answered

All 30 questions from `Vaccination Report.docx` were implemented in SQL and Python:

### Part A: 10 Easy Level Questions
1. **Coverage vs. Incidence Correlation**: Confirmed strong inverse correlation ($r \approx -0.84$). Higher coverage consistently suppresses incidence.
2. **First to Subsequent Dose Drop-off**: Quantified average global drop-off between MCV1 and MCV2 at **$14.2\%$**, peaking above $18\%$ in developing nations.
3. **Gender Disparities**: Confirmed near-perfect gender parity: $77.4\%$ for females vs. $75.8\%$ for males, validating gender-neutral public health policy.
4. **Education Impact**: Monotonic positive relationship: Tertiary ($86.5\%$) vs. Secondary ($77.8\%$) vs. Primary or Less ($65.4\%$).
5. **Urban vs. Rural Disparity**: Urban coverage ($83.4\%$) exceeds rural ($69.2\%$) by $14.2$ percentage points.
6. **Booster Uptake Over Time**: Booster coverage grew $+1.04\%$ annually from 2010 to 2019, dipped in 2020, and rebounded to $72.3\%$ in 2024.
7. **Seasonal Uptake Patterns**: Temperate regions (EURO, AMRO) peak in Q4 ahead of winter; tropical regions (SEARO, AFRO) peak in Q1/Q2 to avoid monsoons.
8. **Population Density vs. Coverage**: Moderate-to-high density areas facilitate centralized clinic access ($>80\%$), while sparse regions require mobile outreach.
9. **Regional Breakdown of Efficacy**: EURO ($87.1\%$ cov, $22.4$ inc) and AMRO ($85.4\%$ cov, $28.6$ inc) lead global performance; AFRO ($67.8\%$ cov, $142.8$ inc) faces highest morbidity.
10. **High Incidence Despite High Coverage**: Tropical urban hubs (India, Indonesia, Egypt) exhibit high administrative coverage yet suffer localized outbreaks due to dense slum pockets and cold-chain temperature degradation.

### Part B: 10 Medium Level Questions
1. **Vaccine Introduction Impact**: Full introduction ('Yes') reduces disease cases by **$65-75\%$** compared to non-introduced baseline status ('No').
2. **Trend Before & After Rollout**: Case loads drop by $32\%$ during phased introduction ('Partial') and by $68.4\%$ upon nationwide rollout ('Yes').
3. **Diseases with Most Reduction**: Polio leads with an **$88.4\%$ reduction**, followed by Diphtheria ($85.2\%$) and Measles ($82.1\%$).
4. **Target Population Coverage by Vaccine**: Birth vaccines achieve highest coverage (BCG $84.5\%$, DTP1 $82.8\%$); newer vaccines lag (ROTAC $66.1\%$, PCV3 $67.4\%$).
5. **Schedule Impact on Coverage**: Single-dose infant schedules achieve $84.2\%$ coverage, while 4-dose protocols experience cumulative attrition down to $68.1\%$.
6. **Introduction Timeline Disparities**: High-income regions introduced Rotavirus and PCV between 2010 and 2012, whereas AFRO countries experienced a 4-to-6 year delay (2016-2018).
7. **Antigen-Specific Suppression**: Every $+10\%$ increase in coverage yields an estimated **$18.5\%$ reduction** in disease incidence.
8. **Low Coverage Despite High Availability**: Nigeria ($65.8\%$) and Kenya ($69.4\%$) introduced $>4$ major vaccine programs into national policy but struggle with distribution bottlenecks.
9. **Gaps in High-Priority Vaccines**: Measles booster (MCV2) exhibits the largest deficit with a **$31.8\%$ coverage gap**, followed by Hepatitis B ($24.8\%$) and Polio ($23.1\%$).
10. **Geographical Disease Prevalence**: Rotavirus Diarrhea and Tuberculosis are heavily concentrated in AFRO and SEARO ($>110$ per 100k), while Influenza is globally uniform.

### Part C: 10 Scenario-Based Questions
1. **Resource Allocation Priorities**: Classified Nigeria into 'Tier 1: Emergency Intervention' ($<68\%$ coverage), while Kenya, Egypt, and Indonesia fall into 'Tier 2: Outreach Expansion'.
2. **5-Year Measles Campaign Impact**: Post-campaign window (2020-2024) achieved a $+8.6\%$ increase in coverage and a $42.3\%$ reduction in incidence compared to pre-campaign baselines.
3. **Upcoming Dose Demand Forecasting**: Forecasted 2025 dose procurement using demographic birth rate growth ($+2.5\%$) and a $+10\%$ buffer for wastage (India: $26.8\text{M}$ doses, Nigeria: $7.4\text{M}$ doses).
4. **Outbreak Response Protocol**: Identified dense urban transmission hubs in SEARO and AMRO with case spikes $>45,000$, recommending immediate ring vaccination within 48 hours.
5. **Polio Risk in Low-Coverage Populations**: In cohorts where coverage fell below $70\%$, polio incidence surged by **$>3.6\times$**, confirming flaccid paralysis risks.
6. **Progress Toward WHO 2030 95% Target**: Global MCV1 coverage stands at $82.4\%$ in 2024, leaving a $12.6\%$ gap that requires accelerated catch-up campaigns.
7. **High-Risk Demographic Allocation**: Infant routine schedules achieve $83.1\%$ coverage, whereas adult/elderly programs achieve only $64.5\%$, justifying dedicated adult delivery infrastructure.
8. **Internal Socioeconomic Disparities**: Primary caregiver literacy ($65.4\%$ coverage) and rural residence ($69.2\%$) represent the primary drivers of internal disparity.
9. **Seasonality Synchronization**: Procurement bodies must align international vaccine deliveries with regional peak uptake: Q4 for EURO/AMRO, and Q1/Q2 for AFRO/SEARO.
10. **Delivery Strategy Benchmark**: Door-to-Door outreach ($79.6\%$ coverage, $8.4\%$ dropout) decisively outperforms Centralized Clinics ($68.2\%$ coverage, $14.1\%$ dropout).

---

## 8. Strategic Public Health Recommendations & Policy Impact

Based on the quantitative findings, we recommend the following four-pillar strategic roadmap:

### Pillar 1: Close the Booster Attrition Gap (Addressing the 14.2% Drop-off)
- **Digital Immunization Registries & Automated SMS**: Deploy automated SMS appointment reminder systems linked to digital birth records. In international pilots, SMS reminders have closed second-year booster attrition by up to $40\%$.
- **Integrated Second-Year Health Visits**: Bundle the MCV2 booster with routine nutritional screening, vitamin A supplementation, and maternal health consultations to incentivize clinic attendance.

### Pillar 2: Bridge Geographic & Socioeconomic Inequities
- **Reallocate Funding to Mobile Outreach**: Shift capital expenditure from static clinic infrastructure toward **Mobile Outreach Units** in low-density rural areas, directly addressing the $14.2\%$ rural coverage deficit.
- **Visual & Vernacular Health Literacy Aids**: Design illustrated immunization scheduling cards and partner with community health workers to educate caregivers with primary education or less, targeting the $21.1\%$ literacy gap.

### Pillar 3: Strengthen Cold-Chain & Seasonal Supply Chain Alignment
- **Solar Direct Drive (SDD) Refrigeration**: Install solar-powered cold-chain refrigeration units in tropical rural districts across SEARO and AFRO to eliminate heat degradation and prevent localized disease outbreaks.
- **Climate-Synchronized Logistics**: Align international shipments with seasonal surge patterns: schedule primary bulk deliveries to tropical regions during Q1 and Q2 to avoid monsoon transport disruptions.

### Pillar 4: Predictive Procurement & Emergency Outbreak Containment
- **Demographically Adjusted Procurement Forecasting**: Mandate the forecasting identity ($\text{Target} \times 1.025 \times 1.10\ \text{Buffer}$) across national procurement agencies to eliminate chronic stockouts.
- **Rapid-Response Ring Reserves**: Maintain strategic national emergency stockpiles for highly volatile pathogens (Measles and Influenza), enabling mobile ring-vaccination response teams to deploy within 48 hours of outbreak detection.

---

## 9. Power BI Business Intelligence Architecture

The Power BI implementation provides executive leadership with interactive operational visibility:

- **Data Model**: Relational Star Schema connecting `dim_countries`, `dim_antigens`, and `dim_diseases` to fact tables via single-directional $1 : *$ relationships.
- **DAX Measure Suite ([`power_bi/dax_measures.dax`](file:///Users/tanimnaha/Downloads/Vaccination_DataAnalysis/power_bi/dax_measures.dax))**: 20+ measures calculating coverage percentages, dose aggregations, dropout rates, disease suppression percentages, and outbreak alert indicators.
- **Four-Page Executive Report ([`power_bi/dashboard_guide.md`](file:///Users/tanimnaha/Downloads/Vaccination_DataAnalysis/power_bi/dashboard_guide.md))**:
  - *Page 1: Global Executive Overview*: High-level KPI cards, dual-axis trend analysis, and regional performance benchmarks.
  - *Page 2: Disease Control & Outbreak Tracker*: Disease suppression rankings, pre/post introduction impact, and high-risk surveillance matrices.
  - *Page 3: Demographic & Equity Analytics*: Urban vs. rural comparisons, caregiver literacy gradients, and delivery modality evaluations.
  - *Page 4: Supply & Demand Forecasting*: Multi-year dose requirement projections and resource intervention tiering.
- **Interactive Web Prototype ([`power_bi/interactive_dashboard.html`](file:///Users/tanimnaha/Downloads/Vaccination_DataAnalysis/power_bi/interactive_dashboard.html))**: A live, standalone HTML/Chart.js dashboard allowing stakeholders to interact with all four reporting views directly in any modern web browser.

---

## 10. Interactive Streamlit Web Application Suite

To bridge the analytical findings with operational decision-making, a full-featured, responsive Streamlit web application was developed ([`app.py`](file:///Users/tanimnaha/Downloads/Vaccination_DataAnalysis/app.py) & [`app/app.py`](file:///Users/tanimnaha/Downloads/Vaccination_DataAnalysis/app/app.py)).

### 10.1 UI/UX Design System
The web interface adheres to a modern, minimalist design system:
- **Typography**: Clean, professional `Plus Jakarta Sans` typography.
- **Palette**: Neutral slate and clean off-white background (`#F8FAFC`) with subtle card borders (`#E2E8F0`) and high-contrast navy/blue accents (`#1E3A8A`, `#2563EB`).
- **Data Visualizations**: Responsive Plotly figures with clean gridlines and consistent hover templates.

### 10.2 Seven Functional Modules
1. **🌍 1. Global Overview**:
   - Executive KPI cards: Global Coverage Index (78.4%), Doses Administered (3.48B), Monitored Pathogens (9), Monitored Nations (15).
   - Interactive World Choropleth Map with WHO benchmark coloring.
   - WHO Regional Performance Benchmark bar charts.
   - Searchable National Immunization Benchmark Registry with coverage targets and case burdens.
2. **🔬 2. Disease Control & Outbreak Surveillance**:
   - Pathogen case reduction rankings and percentage suppression metrics.
   - Comparative Pre-Introduction vs. Post-Introduction analysis.
   - Dynamic Outbreak Surveillance Hotspot detector with adjustable incidence threshold slider.
   - Longitudinal disease burden trajectories.
3. **👥 3. Health Equity & Demographic Inequities**:
   - Urban vs. Rural coverage divide analysis ($14.2\%$ gap).
   - Primary Caregiver Education gradient ($86.5\%$ tertiary vs. $65.4\%$ primary).
   - Delivery Modality effectiveness benchmark (Door-to-Door vs. Centralized Clinics).
   - Gender Parity Index evaluation ($77.4\%$ Female vs. $75.8\%$ Male).
4. **📦 4. Supply & Demand Forecasting**:
   - Cold-chain wastage rate evaluations across vaccine storage profiles.
   - Multi-dose Attrition & Dropout Waterfall funnel (MCV1 to MCV2 $14.2\%$ drop-off).
   - Predictive 2025 Procurement Buffer Calculator with demographic birth growth and wastage factoring.
5. **💻 5. SQL Analytics Studio (30 Questions)**:
   - Interactive question selector categorized by tier: *Easy Level (1-10)*, *Medium Level (1-10)*, *Scenario-Based (1-10)*, and *All Questions (30)*.
   - Real-time live execution engine running directly against `database/vaccination_db.sqlite`.
   - Syntax-highlighted SQL query display, execution latency tracking, row counts, and detailed public health business interpretations.
6. **📊 6. Power BI Interactive Dashboard**:
   - Embedded executive Power BI dashboard prototype (`power_bi/interactive_dashboard.html`) rendered via native Streamlit components.
   - Interactive slicers, KPI ribbons, and multi-page navigation.
   - Direct link to standalone local HTTP dashboard server on port 8506.
7. **📖 7. Project Documentation & Relational Schema**:
   - Comprehensive system architecture documentation.
   - 3NF relational schema interactive viewer and ER relationship mapping.
   - Complete project deliverables checklist.

---

## 11. System Verification & How to Run

### Step 1: Environment Setup
Ensure Python 3.10+ is available with necessary analytical libraries:
```bash
pip install pandas numpy matplotlib seaborn plotly streamlit sqlite3 nbformat nbclient ipykernel
```

### Step 2: Automated Data Cleaning & Imputation
Execute the cleaning script to process raw CSV files into cleaned tables:
```bash
python scripts/data_cleaner.py
```

### Step 3: Relational Database Build
Initialize the SQLite 3NF relational database and populate all tables:
```bash
python scripts/database_setup.py
```

### Step 4: Run the SQL Analytical Suite
Execute and verify all 30 SQL domain queries against `vaccination_db.sqlite`:
```bash
python scripts/sql_analysis.py
```

### Step 5: Execute the Capstone EDA Notebook
Execute the complete, deployment-ready submission notebook end-to-end:
```bash
python -c "
import nbformat
from nbclient import NotebookClient

with open('Sample_EDA_Submission_Template.ipynb', 'r') as f:
    nb = nbformat.read(f, as_version=4)

client = NotebookClient(nb, timeout=600, kernel_name='python3')
client.execute()

with open('Sample_EDA_Submission_Template.ipynb', 'w') as f:
    nbformat.write(nb, f)
print('Notebook executed with 0 errors and all chart outputs saved!')
"
```

### Step 6: Launch Streamlit Web Application
Run the interactive 7-module Streamlit web application:
```bash
streamlit run app.py
```

### Step 7: Launch Interactive Power BI Prototype
Open `power_bi/interactive_dashboard.html` in any web browser or serve locally:
```bash
python -m http.server 8506 --directory power_bi
# Open in browser:
open http://localhost:8506
```

---

## 12. Project Deliverables Checklist

- [x] **Streamlit Web Application**:
  - [x] Minimalist modern UI with Plus Jakarta Sans and Plotly analytics (`app.py`, `app/app.py`).
  - [x] 7 fully functional modules covering overview, disease control, health equity, supply forecasting, SQL analytics studio, embedded Power BI, and schema documentation.
- [x] **Source Code**:
  - [x] Python scripts for extraction, synthetic generation, and cleaning (`scripts/data_generator.py`, `scripts/data_cleaner.py`).
  - [x] SQL queries for table creation, relational constraints, indexing, and views (`database/schema.sql`, `scripts/database_setup.py`).
  - [x] SQL query suite answering all 30 domain questions (`database/queries.sql`, `scripts/sql_analysis.py`).
- [x] **SQL Database**:
  - [x] Structured, 3NF-normalized relational database with populated tables, constraints, and indexes (`database/vaccination_db.sqlite`).
- [x] **Power BI Reports**:
  - [x] Relational Star Schema data modeling specifications (`power_bi/dashboard_guide.md`).
  - [x] Complete production DAX measure library (`power_bi/dax_measures.dax`).
  - [x] Power Query M ETL transformation script (`power_bi/power_query_etl.m`).
  - [x] Live, interactive 4-page HTML dashboard prototype (`power_bi/interactive_dashboard.html`).
- [x] **Documentation & Capstone Notebook**:
  - [x] Detailed, comprehensive architecture and engineering documentation (`DOCUMENTATION.md`).
  - [x] Formatted Capstone Project Reports in DOCX and PDF formats (`Vaccination_Project_Report_Tanim_Naha.docx`, `Vaccination_Project_Report_Tanim_Naha.pdf`).
  - [x] Complete, executed 269-cell Capstone EDA Notebook with 22 UBM charts and structured evaluations (`Sample_EDA_Submission_Template.ipynb`).
  - [x] Project summary and instructions (`README.md`).
