import os
import pandas as pd
import numpy as np

def clean_data():
    raw_dir = "data/raw"
    clean_dir = "data/cleaned"
    os.makedirs(clean_dir, exist_ok=True)

    print("Cleaning Table 1: coverage_data.csv...")
    cov_path = os.path.join(raw_dir, "coverage_data.csv")
    if os.path.exists(cov_path):
        df_cov = pd.read_csv(cov_path)
        
        # Strip '%' if present and convert Coverage to numeric float
        df_cov['Coverage_Pct'] = df_cov['Coverage'].astype(str).str.replace('%', '', regex=False)
        df_cov['Coverage_Pct'] = pd.to_numeric(df_cov['Coverage_Pct'], errors='coerce')
        
        # Ensure Target_number and Dodge are numeric
        df_cov['Target_number'] = pd.to_numeric(df_cov['Target_number'], errors='coerce')
        df_cov['Dodge'] = pd.to_numeric(df_cov['Dodge'], errors='coerce')
        
        # Impute missing Target_number where possible: Target_number = Dodge / (Coverage_Pct / 100)
        mask_missing_target = df_cov['Target_number'].isna() & (df_cov['Coverage_Pct'] > 0)
        df_cov.loc[mask_missing_target, 'Target_number'] = (
            df_cov.loc[mask_missing_target, 'Dodge'] / (df_cov.loc[mask_missing_target, 'Coverage_Pct'] / 100.0)
        )
        
        # Fill any remaining missing Target_number with country-antigen median
        df_cov['Target_number'] = df_cov.groupby(['Code', 'Antigen'])['Target_number'].transform(
            lambda x: x.fillna(x.median())
        )
        df_cov['Target_number'] = df_cov['Target_number'].fillna(df_cov['Target_number'].median())
        
        # Cap Coverage_Pct within valid 0 - 100 range
        df_cov['Coverage_Pct'] = df_cov['Coverage_Pct'].clip(lower=0.0, upper=100.0)
        
        # Drop original raw Coverage string column and rename clean column
        df_cov = df_cov.drop(columns=['Coverage'])
        
        df_cov.to_csv(os.path.join(clean_dir, "coverage_data_clean.csv"), index=False)
        print(f"Coverage data cleaned: {len(df_cov)} rows.")

    print("Cleaning Table 2: incidence_rate.csv...")
    inc_path = os.path.join(raw_dir, "incidence_rate.csv")
    if os.path.exists(inc_path):
        df_inc = pd.read_csv(inc_path)
        df_inc['Incidence_rate'] = pd.to_numeric(df_inc['Incidence_rate'], errors='coerce').fillna(0.0)
        df_inc['Incidence_rate'] = df_inc['Incidence_rate'].clip(lower=0.0)
        df_inc.to_csv(os.path.join(clean_dir, "incidence_rate_clean.csv"), index=False)
        print(f"Incidence rate data cleaned: {len(df_inc)} rows.")

    print("Cleaning Table 3: reported_cases.csv...")
    cases_path = os.path.join(raw_dir, "reported_cases.csv")
    if os.path.exists(cases_path):
        df_cases = pd.read_csv(cases_path)
        df_cases['Cases'] = pd.to_numeric(df_cases['Cases'], errors='coerce').fillna(0).astype(int)
        df_cases['Cases'] = df_cases['Cases'].clip(lower=0)
        df_cases.to_csv(os.path.join(clean_dir, "reported_cases_clean.csv"), index=False)
        print(f"Reported cases data cleaned: {len(df_cases)} rows.")

    print("Cleaning Table 4: vaccine_introduction.csv...")
    intro_path = os.path.join(raw_dir, "vaccine_introduction.csv")
    if os.path.exists(intro_path):
        df_intro = pd.read_csv(intro_path)
        df_intro['Intro'] = df_intro['Intro'].astype(str).str.strip().str.capitalize()
        df_intro.to_csv(os.path.join(clean_dir, "vaccine_introduction_clean.csv"), index=False)
        print(f"Vaccine introduction data cleaned: {len(df_intro)} rows.")

    print("Cleaning Table 5: vaccine_schedule.csv...")
    sch_path = os.path.join(raw_dir, "vaccine_schedule.csv")
    if os.path.exists(sch_path):
        df_sch = pd.read_csv(sch_path)
        for col in df_sch.select_dtypes(include='object').columns:
            df_sch[col] = df_sch[col].astype(str).str.strip()
        df_sch.to_csv(os.path.join(clean_dir, "vaccine_schedule_clean.csv"), index=False)
        print(f"Vaccine schedule data cleaned: {len(df_sch)} rows.")

    print("Cleaning Table 6: socioeconomic_metrics.csv...")
    socio_path = os.path.join(raw_dir, "socioeconomic_metrics.csv")
    if os.path.exists(socio_path):
        df_socio = pd.read_csv(socio_path)
        df_socio['Coverage_Pct'] = pd.to_numeric(df_socio['Coverage_Pct'], errors='coerce').clip(0.0, 100.0)
        df_socio['Dropout_Rate_Pct'] = pd.to_numeric(df_socio['Dropout_Rate_Pct'], errors='coerce').clip(0.0, 100.0)
        df_socio['Population_Density_sqkm'] = pd.to_numeric(df_socio['Population_Density_sqkm'], errors='coerce')
        df_socio.to_csv(os.path.join(clean_dir, "socioeconomic_metrics_clean.csv"), index=False)
        print(f"Socioeconomic metrics data cleaned: {len(df_socio)} rows.")

    print("Data cleaning process successfully completed!")

if __name__ == "__main__":
    clean_data()
