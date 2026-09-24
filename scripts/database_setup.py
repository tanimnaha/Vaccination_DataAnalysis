import os
import sqlite3
import pandas as pd

def build_database():
    db_dir = "database"
    clean_dir = "data/cleaned"
    os.makedirs(db_dir, exist_ok=True)
    
    db_path = os.path.join(db_dir, "vaccination_db.sqlite")
    schema_path = os.path.join(db_dir, "schema.sql")
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    print(f"Connecting to SQLite database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read and execute DDL schema
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()
    print("Database schema successfully applied.")
    
    # -------------------------------------------------------------------------
    # 1. Populate Dimension Tables
    # -------------------------------------------------------------------------
    print("Populating Dimension Tables...")
    
    # Extract unique countries from cleaned coverage data + metadata
    COUNTRIES_META = [
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
    df_dim_countries = pd.DataFrame(COUNTRIES_META).rename(columns={
        "code": "country_code", "name": "country_name", "region": "who_region",
        "density": "population_density_sqkm", "income": "income_group"
    })
    df_dim_countries.to_sql("dim_countries", conn, if_exists="append", index=False)
    
    # Extract unique Antigens
    ANTIGENS_META = [
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
    df_dim_antigens = pd.DataFrame(ANTIGENS_META).rename(columns={
        "code": "antigen_code", "desc": "antigen_description", "disease": "target_disease_code"
    })
    df_dim_antigens.to_sql("dim_antigens", conn, if_exists="append", index=False)
    
    # Extract unique Diseases
    DISEASES_META = [
        {"code": "MEASLES", "desc": "Measles", "denom": "Per 100,000 population"},
        {"code": "PERTUSSIS", "desc": "Pertussis (Whooping Cough)", "denom": "Per 100,000 population"},
        {"code": "DIPHTHERIA", "desc": "Diphtheria", "denom": "Per 100,000 population"},
        {"code": "TETANUS", "desc": "Neonatal Tetanus", "denom": "Per 1,000 live births"},
        {"code": "POLIO", "desc": "Poliomyelitis", "denom": "Per 100,000 population"},
        {"code": "HEPB", "desc": "Hepatitis B", "denom": "Per 100,000 population"},
        {"code": "TUBERCULOSIS", "desc": "Tuberculosis", "denom": "Per 100,000 population"},
        {"code": "ROTA_DIARRHEA", "desc": "Rotavirus Diarrhea", "denom": "Per 100,000 population"},
        {"code": "INFLUENZA", "desc": "Seasonal Influenza", "denom": "Per 100,000 population"},
        {"code": "HPV_CANCER", "desc": "Cervical Cancer (HPV)", "denom": "Per 100,000 population"}
    ]
    df_dim_diseases = pd.DataFrame(DISEASES_META).rename(columns={
        "code": "disease_code", "desc": "disease_description", "denom": "denominator_unit"
    })
    df_dim_diseases.to_sql("dim_diseases", conn, if_exists="append", index=False)
    
    # -------------------------------------------------------------------------
    # 2. Populate Fact Tables
    # -------------------------------------------------------------------------
    print("Populating Fact Tables...")
    
    # fact_coverage
    df_cov = pd.read_csv(os.path.join(clean_dir, "coverage_data_clean.csv"))
    df_cov_fact = df_cov[['Code', 'Year', 'Antigen', 'Coverage_category', 'Coverage_category_description', 'Target_number', 'Dodge', 'Coverage_Pct']].copy()
    df_cov_fact.columns = ['country_code', 'year', 'antigen_code', 'coverage_category', 'coverage_category_description', 'target_number', 'doses_administered', 'coverage_pct']
    df_cov_fact.to_sql("fact_coverage", conn, if_exists="append", index=False)
    
    # fact_incidence
    df_inc = pd.read_csv(os.path.join(clean_dir, "incidence_rate_clean.csv"))
    df_inc_fact = df_inc[['Code', 'Year', 'Disease', 'Denominator', 'Incidence_rate']].copy()
    df_inc_fact.columns = ['country_code', 'year', 'disease_code', 'denominator_unit', 'incidence_rate']
    df_inc_fact.to_sql("fact_incidence", conn, if_exists="append", index=False)
    
    # fact_reported_cases
    df_cases = pd.read_csv(os.path.join(clean_dir, "reported_cases_clean.csv"))
    df_cases_fact = df_cases[['Code', 'Year', 'Disease', 'Cases']].copy()
    df_cases_fact.columns = ['country_code', 'year', 'disease_code', 'reported_cases']
    df_cases_fact.to_sql("fact_reported_cases", conn, if_exists="append", index=False)
    
    # fact_vaccine_intro
    df_intro = pd.read_csv(os.path.join(clean_dir, "vaccine_introduction_clean.csv"))
    df_intro_fact = df_intro[['ISO_3_Code', 'Year', 'Description', 'Intro']].copy()
    df_intro_fact.columns = ['country_code', 'year', 'vaccine_description', 'intro_status']
    df_intro_fact.to_sql("fact_vaccine_intro", conn, if_exists="append", index=False)
    
    # fact_vaccine_schedule
    df_sch = pd.read_csv(os.path.join(clean_dir, "vaccine_schedule_clean.csv"))
    df_sch_fact = df_sch[['ISO_3_Code', 'Year', 'Vaccine_code', 'Vaccine_description', 'Schedule_rounds', 'Target_pop', 'Target_pop_description', 'Geoarea', 'Age_administered', 'Source_comment']].copy()
    df_sch_fact.columns = ['country_code', 'year', 'vaccine_code', 'vaccine_description', 'schedule_rounds', 'target_pop', 'target_pop_description', 'geo_area', 'age_administered', 'source_comment']
    df_sch_fact.to_sql("fact_vaccine_schedule", conn, if_exists="append", index=False)
    
    # fact_socioeconomic
    df_socio = pd.read_csv(os.path.join(clean_dir, "socioeconomic_metrics_clean.csv"))
    df_socio_fact = df_socio[['ISO_3_Code', 'Year', 'Dimension', 'Subgroup', 'Coverage_Pct', 'Dropout_Rate_Pct', 'Population_Density_sqkm', 'Vaccination_Strategy', 'Seasonal_Peak_Quarter']].copy()
    df_socio_fact.columns = ['country_code', 'year', 'dimension', 'subgroup', 'coverage_pct', 'dropout_rate_pct', 'population_density_sqkm', 'vaccination_strategy', 'seasonal_peak_quarter']
    df_socio_fact.to_sql("fact_socioeconomic", conn, if_exists="append", index=False)
    
    conn.commit()
    
    # -------------------------------------------------------------------------
    # 3. Verification & Table Row Counts
    # -------------------------------------------------------------------------
    print("\nDatabase Build Verification Summary:")
    tables = [
        "dim_countries", "dim_antigens", "dim_diseases",
        "fact_coverage", "fact_incidence", "fact_reported_cases",
        "fact_vaccine_intro", "fact_vaccine_schedule", "fact_socioeconomic"
    ]
    for table in tables:
        count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f" - Table {table:25s}: {count:5d} records")
        
    conn.close()
    print("\nDatabase setup complete!")

if __name__ == "__main__":
    build_database()
