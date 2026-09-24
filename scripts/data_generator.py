import os
import numpy as np
import pandas as pd

# Set random seed for reproducible synthetic data generation
np.random.seed(42)

# Ensure directory structures exist
os.makedirs("data/raw", exist_ok=True)

# Define reference metadata
COUNTRIES = [
    {"code": "IND", "name": "India", "region": "SEARO", "density": 435, "income": "Lower-middle"},
    {"code": "USA", "name": "United States", "region": "AMRO", "density": 37, "income": "High"},
    {"code": "BRA", "name": "Brazil", "region": "AMRO", "density": 25, "income": "Upper-middle"},
    {"code": "NGA", "name": "Nigeria", "region": "AFRO", "density": 226, "income": "Lower-middle"},
    {"code": "DEU", "name": "Germany", "region": "EURO", "density": 240, "income": "High"},
    {"code": "CHN", "name": "China", "region": "WPRO", "density": 150, "income": "Upper-middle"},
    {"code": "KEN", "name": "Kenya", "region": "AFRO", "density": 94, "income": "Lower-middle"},
    {"code": "IDN", "name": "Indonesia", "region": "SEARO", "density": 145, "income": "Upper-middle"},
    {"code": "EGY", "name": "Egypt", "region": "EMRO", "density": 103, "income": "Lower-middle"},
    {"code": "ZAF", "name": "South Africa", "region": "AFRO", "density": 49, "income": "Upper-middle"},
    {"code": "GBR", "name": "United Kingdom", "region": "EURO", "density": 277, "income": "High"},
    {"code": "JPN", "name": "Japan", "region": "WPRO", "density": 338, "income": "High"},
    {"code": "MEX", "name": "Mexico", "region": "AMRO", "density": 66, "income": "Upper-middle"},
    {"code": "PAK", "name": "Pakistan", "region": "EMRO", "density": 287, "income": "Lower-middle"},
    {"code": "BGD", "name": "Bangladesh", "region": "SEARO", "density": 1265, "income": "Lower-middle"}
]

YEARS = list(range(2010, 2025))

ANTIGENS = [
    {"code": "MCV1", "desc": "Measles 1st Dose", "disease": "MEASLES"},
    {"code": "MCV2", "desc": "Measles 2nd Dose", "disease": "MEASLES"},
    {"code": "DTP1", "desc": "Diphtheria-Tetanus-Pertussis 1st Dose", "disease": "PERTUSSIS"},
    {"code": "DTP3", "desc": "Diphtheria-Tetanus-Pertussis 3rd Dose", "disease": "PERTUSSIS"},
    {"code": "BCG", "desc": "Bacillus Calmette-Guérin (Tuberculosis)", "disease": "TUBERCULOSIS"},
    {"code": "HEPB3", "desc": "Hepatitis B 3rd Dose", "disease": "HEPB"},
    {"code": "POL3", "desc": "Polio 3rd Dose", "disease": "POLIO"},
    {"code": "ROTA", "desc": "Rotavirus Last Dose", "disease": "ROTA_DIARRHEA"},
    {"code": "IPV1", "desc": "Inactivated Polio 1st Dose", "disease": "POLIO"},
    {"code": "HPV", "desc": "Human Papillomavirus Last Dose", "disease": "HPV_CANCER"}
]

DISEASES = [
    {"code": "MEASLES", "desc": "Measles", "denom": "Per 100,000 population", "base_incidence": 120},
    {"code": "PERTUSSIS", "desc": "Pertussis (Whooping Cough)", "denom": "Per 100,000 population", "base_incidence": 85},
    {"code": "DIPHTHERIA", "desc": "Diphtheria", "denom": "Per 100,000 population", "base_incidence": 15},
    {"code": "TETANUS", "desc": "Neonatal Tetanus", "denom": "Per 1,000 live births", "base_incidence": 8},
    {"code": "POLIO", "desc": "Poliomyelitis", "denom": "Per 100,000 population", "base_incidence": 25},
    {"code": "HEPB", "desc": "Hepatitis B", "denom": "Per 100,000 population", "base_incidence": 90},
    {"code": "TUBERCULOSIS", "desc": "Tuberculosis", "denom": "Per 100,000 population", "base_incidence": 210},
    {"code": "ROTA_DIARRHEA", "desc": "Rotavirus Diarrhea", "denom": "Per 100,000 population", "base_incidence": 350},
    {"code": "INFLUENZA", "desc": "Seasonal Influenza", "denom": "Per 100,000 population", "base_incidence": 450}
]

# -------------------------------------------------------------
# 1. Generate Table 1: coverage_data.csv
# -------------------------------------------------------------
print("Generating Table 1: coverage_data.csv...")
coverage_rows = []

for c in COUNTRIES:
    # Baseline coverage level based on region / income
    base_cov = 88.0 if c["income"] == "High" else (78.0 if c["income"] == "Upper-middle" else 65.0)
    # Annual target population based on country
    target_base = int(np.random.randint(200000, 20000000))
    
    for yr in YEARS:
        # Time trend improvement over years, with COVID-19 dip in 2020-2021
        year_modifier = (yr - 2010) * 0.8
        if yr in [2020, 2021]:
            year_modifier -= 6.5
            
        for ag in ANTIGENS:
            # First doses generally higher coverage than multi-dose boosters
            antigen_mod = 0.0
            if ag["code"] in ["MCV1", "DTP1", "BCG"]:
                antigen_mod = 6.0
            elif ag["code"] in ["MCV2", "DTP3", "HPV"]:
                antigen_mod = -8.0
            
            coverage_pct = base_cov + year_modifier + antigen_mod + np.random.normal(0, 3.5)
            coverage_pct = max(15.0, min(99.0, coverage_pct))
            
            target_num = int(target_base * (1 + (yr - 2010)*0.01 + np.random.normal(0, 0.02)))
            doses = int(target_num * (coverage_pct / 100.0))
            
            cat = "OFFICIAL" if yr % 2 == 0 else "ADMINISTRATIVE"
            cat_desc = "Official WHO/UNICEF estimate" if cat == "OFFICIAL" else "Administrative reports from health facilities"
            
            # Intentionally insert a few uncleaned noise artifacts for data wrangling demonstration
            cov_val_str = f"{coverage_pct:.1f}%" if np.random.rand() < 0.05 else round(coverage_pct, 2)
            
            coverage_rows.append({
                "Group": "Countries",
                "Code": c["code"],
                "Name": c["name"],
                "Year": yr,
                "Antigen": ag["code"],
                "Antigen_description": ag["desc"],
                "Coverage_category": cat,
                "Coverage_category_description": cat_desc,
                "Target_number": target_num if np.random.rand() > 0.02 else np.nan, # missing value simulation
                "Dodge": doses,
                "Coverage": cov_val_str
            })

df_coverage = pd.DataFrame(coverage_rows)
df_coverage.to_csv("data/raw/coverage_data.csv", index=False)

# -------------------------------------------------------------
# 2. Generate Table 2: incidence_rate.csv
# -------------------------------------------------------------
print("Generating Table 2: incidence_rate.csv...")
incidence_rows = []

for c in COUNTRIES:
    for yr in YEARS:
        # Fetch approximate average coverage for that country/year
        yr_cov = df_coverage[(df_coverage["Code"] == c["code"]) & (df_coverage["Year"] == yr)]["Coverage"]
        # numeric conversion helper
        numeric_covs = []
        for val in yr_cov:
            try:
                numeric_covs.append(float(str(val).replace('%','')))
            except:
                pass
        mean_cov = np.mean(numeric_covs) if len(numeric_covs) > 0 else 70.0
        
        for d in DISEASES:
            # Strong inverse correlation between coverage and incidence rate!
            cov_effect = (100.0 - mean_cov) / 30.0
            inc_rate = d["base_incidence"] * (0.35 ** ((mean_cov - 50) / 20.0)) + np.random.normal(0, 5)
            if c["income"] == "High":
                inc_rate *= 0.2
            elif c["income"] == "Lower-middle":
                inc_rate *= 1.4
                
            inc_rate = max(0.1, round(inc_rate, 2))
            
            incidence_rows.append({
                "Group": "Countries",
                "Code": c["code"],
                "Name": c["name"],
                "Year": yr,
                "Disease": d["code"],
                "Disease_description": d["desc"],
                "Denominator": d["denom"],
                "Incidence_rate": inc_rate
            })

df_incidence = pd.DataFrame(incidence_rows)
df_incidence.to_csv("data/raw/incidence_rate.csv", index=False)

# -------------------------------------------------------------
# 3. Generate Table 3: reported_cases.csv
# -------------------------------------------------------------
print("Generating Table 3: reported_cases.csv...")
cases_rows = []

for c in COUNTRIES:
    # Pop estimate factor
    pop_factor = 1400 if c["code"] in ["IND", "CHN"] else (330 if c["code"] == "USA" else 100)
    
    for yr in YEARS:
        for d in DISEASES:
            # Find matching incidence rate
            match_inc = df_incidence[
                (df_incidence["Code"] == c["code"]) & 
                (df_incidence["Year"] == yr) & 
                (df_incidence["Disease"] == d["code"])
            ]
            inc_val = match_inc["Incidence_rate"].values[0] if len(match_inc) > 0 else 10.0
            
            cases = int(inc_val * pop_factor * (1 + np.random.normal(0, 0.15)))
            cases = max(0, cases)
            
            # Simulate 5-year measles outbreak spike for scenario-based question!
            if c["code"] == "NGA" and yr == 2018 and d["code"] == "MEASLES":
                cases = int(cases * 4.5)
            if c["code"] == "KEN" and yr == 2022 and d["code"] == "INFLUENZA":
                cases = int(cases * 5.2) # Influenza sudden outbreak
                
            cases_rows.append({
                "Group": "Countries",
                "Code": c["code"],
                "Name": c["name"],
                "Year": yr,
                "Disease": d["code"],
                "Disease_description": d["desc"],
                "Cases": cases
            })

df_cases = pd.DataFrame(cases_rows)
df_cases.to_csv("data/raw/reported_cases.csv", index=False)

# -------------------------------------------------------------
# 4. Generate Table 4: vaccine_introduction.csv
# -------------------------------------------------------------
print("Generating Table 4: vaccine_introduction.csv...")
intro_vaccines = [
    {"desc": "Rotavirus vaccine", "start_year": 2012},
    {"desc": "IPV - Inactivated Polio Vaccine", "start_year": 2015},
    {"desc": "HPV - Human Papillomavirus Vaccine", "start_year": 2014},
    {"desc": "Pneumococcal Conjugate Vaccine (PCV)", "start_year": 2011},
    {"desc": "COVID-19 Vaccine", "start_year": 2021},
    {"desc": "Malaria Vaccine (RTS,S)", "start_year": 2022}
]

intro_rows = []
for c in COUNTRIES:
    for vac in intro_vaccines:
        # High income countries introduce vaccines earlier than lower-middle income
        delay = 0 if c["income"] == "High" else (2 if c["income"] == "Upper-middle" else 4)
        intro_yr = vac["start_year"] + delay
        
        for yr in YEARS:
            if yr < intro_yr:
                intro_status = "No"
            elif yr == intro_yr:
                intro_status = "Partial"
            else:
                intro_status = "Yes"
                
            intro_rows.append({
                "ISO_3_Code": c["code"],
                "Country_Name": c["name"],
                "Who_Region": c["region"],
                "Year": yr,
                "Description": vac["desc"],
                "Intro": intro_status
            })

df_intro = pd.DataFrame(intro_rows)
df_intro.to_csv("data/raw/vaccine_introduction.csv", index=False)

# -------------------------------------------------------------
# 5. Generate Table 5: vaccine_schedule.csv
# -------------------------------------------------------------
print("Generating Table 5: vaccine_schedule.csv...")
schedule_definitions = [
    {"code": "BCG", "desc": "BCG Vaccine", "round": "Round 1", "pop": "Infants < 1 yr", "pop_desc": "Newborn infants", "age": "At birth"},
    {"code": "DTP1", "desc": "DTP 1st Dose", "round": "Round 1", "pop": "Infants < 1 yr", "pop_desc": "Infants 6 weeks", "age": "6 weeks"},
    {"code": "DTP3", "desc": "DTP 3rd Dose", "round": "Round 3", "pop": "Infants < 1 yr", "pop_desc": "Infants 14 weeks", "age": "14 weeks"},
    {"code": "MCV1", "desc": "Measles 1st Dose", "round": "Round 1", "pop": "Infants < 1 yr", "pop_desc": "Infants 9 months", "age": "9 months"},
    {"code": "MCV2", "desc": "Measles 2nd Dose", "round": "Round 2 (Booster)", "pop": "Children 1-2 yrs", "pop_desc": "Children 15-18 months", "age": "15 months"},
    {"code": "HPV1", "desc": "HPV 1st Dose", "round": "Round 1", "pop": "Adolescent Females", "pop_desc": "Girls 9-14 years", "age": "9 years"},
    {"code": "FLU_ANNUAL", "desc": "Seasonal Flu Booster", "round": "Annual Booster", "pop": "Elderly & High-risk", "pop_desc": "Adults > 65 yrs and vulnerable", "age": "65+ years"}
]

schedule_rows = []
for c in COUNTRIES:
    for sch in schedule_definitions:
        for yr in YEARS:
            schedule_rows.append({
                "ISO_3_Code": c["code"],
                "Country_Name": c["name"],
                "Who_Region": c["region"],
                "Year": yr,
                "Vaccine_code": sch["code"],
                "Vaccine_description": sch["desc"],
                "Schedule_rounds": sch["round"],
                "Target_pop": sch["pop"],
                "Target_pop_description": sch["pop_desc"],
                "Geoarea": "National",
                "Age_administered": sch["age"],
                "Source_comment": "WHO EPI / NITAG National Guidelines"
            })

df_schedule = pd.DataFrame(schedule_rows)
df_schedule.to_csv("data/raw/vaccine_schedule.csv", index=False)

# -------------------------------------------------------------
# 6. Generate Socioeconomic & Demographic Breakdown Data
# -------------------------------------------------------------
print("Generating Table 6: socioeconomic_metrics.csv...")
socio_rows = []

for c in COUNTRIES:
    for yr in YEARS:
        # Base stats
        base_cov = 88.0 if c["income"] == "High" else (75.0 if c["income"] == "Upper-middle" else 62.0)
        base_cov += (yr - 2010) * 0.7
        
        # Gender breakdown (generally slight/minimal disparity, but female slightly higher uptake in adolescent HPV/maternal tet)
        for g in ["Female", "Male"]:
            g_cov = base_cov + (0.8 if g == "Female" else -0.8) + np.random.normal(0, 1.0)
            socio_rows.append({
                "ISO_3_Code": c["code"],
                "Country_Name": c["name"],
                "Who_Region": c["region"],
                "Year": yr,
                "Dimension": "Gender",
                "Subgroup": g,
                "Coverage_Pct": max(10, min(99, round(g_cov, 2))),
                "Dropout_Rate_Pct": max(2, min(35, round(100 - g_cov * 0.9, 2))),
                "Population_Density_sqkm": c["density"],
                "Vaccination_Strategy": "Centralized Health Clinic",
                "Seasonal_Peak_Quarter": "Q4" if c["region"] in ["EURO", "AMRO"] else "Q1"
            })
            
        # Urban vs Rural breakdown (Urban consistently 8-15% higher than rural)
        for ur in ["Urban", "Rural"]:
            ur_cov = base_cov + (6.5 if ur == "Urban" else -7.5) + np.random.normal(0, 1.2)
            strategy = "Centralized Health Clinic" if ur == "Urban" else "Door-to-Door Campaign"
            socio_rows.append({
                "ISO_3_Code": c["code"],
                "Country_Name": c["name"],
                "Who_Region": c["region"],
                "Year": yr,
                "Dimension": "Urban_Rural",
                "Subgroup": ur,
                "Coverage_Pct": max(10, min(99, round(ur_cov, 2))),
                "Dropout_Rate_Pct": max(2, min(35, round(100 - ur_cov * 0.85, 2))),
                "Population_Density_sqkm": c["density"],
                "Vaccination_Strategy": strategy,
                "Seasonal_Peak_Quarter": "Q4" if c["region"] in ["EURO", "AMRO"] else "Q1"
            })
            
        # Education Level breakdown (Tertiary > Secondary > Primary)
        for ed in ["Primary or Less", "Secondary", "Tertiary"]:
            ed_mod = -10.0 if ed == "Primary or Less" else (2.0 if ed == "Secondary" else 11.0)
            ed_cov = base_cov + ed_mod + np.random.normal(0, 1.5)
            socio_rows.append({
                "ISO_3_Code": c["code"],
                "Country_Name": c["name"],
                "Who_Region": c["region"],
                "Year": yr,
                "Dimension": "Education_Level",
                "Subgroup": ed,
                "Coverage_Pct": max(10, min(99, round(ed_cov, 2))),
                "Dropout_Rate_Pct": max(2, min(35, round(100 - ed_cov * 0.88, 2))),
                "Population_Density_sqkm": c["density"],
                "Vaccination_Strategy": "Mobile Outreach Unit",
                "Seasonal_Peak_Quarter": "Q4" if c["region"] in ["EURO", "AMRO"] else "Q1"
            })

df_socio = pd.DataFrame(socio_rows)
df_socio.to_csv("data/raw/socioeconomic_metrics.csv", index=False)

print("Data Generation Complete! All 6 CSV files successfully generated in data/raw/.")
