-- ============================================================================
-- Relational Database Schema: Vaccination Data Analysis and Visualization
-- Database Engine: SQLite3
-- Standard: 3NF Normalized Relational Schema with Foreign Keys & Analytical Views
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- Dimension 1: dim_countries
-- Stores unique country entity metadata including WHO region, density, and income
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS dim_countries;
CREATE TABLE dim_countries (
    country_code VARCHAR(3) PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL,
    who_region VARCHAR(10) NOT NULL,
    population_density_sqkm REAL,
    income_group VARCHAR(50)
);

-- ----------------------------------------------------------------------------
-- Dimension 2: dim_antigens
-- Stores unique vaccine antigen definitions and target disease mapping
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS dim_antigens;
CREATE TABLE dim_antigens (
    antigen_code VARCHAR(20) PRIMARY KEY,
    antigen_description VARCHAR(150) NOT NULL,
    target_disease_code VARCHAR(20)
);

-- ----------------------------------------------------------------------------
-- Dimension 3: dim_diseases
-- Stores unique epidemiological disease definitions and baseline incidence units
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS dim_diseases;
CREATE TABLE dim_diseases (
    disease_code VARCHAR(20) PRIMARY KEY,
    disease_description VARCHAR(150) NOT NULL,
    denominator_unit VARCHAR(100) NOT NULL
);

-- ----------------------------------------------------------------------------
-- Fact 1: fact_coverage
-- Stores annual vaccine administration and population coverage percentages
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS fact_coverage;
CREATE TABLE fact_coverage (
    coverage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_code VARCHAR(3) NOT NULL,
    year INTEGER NOT NULL,
    antigen_code VARCHAR(20) NOT NULL,
    coverage_category VARCHAR(50),
    coverage_category_description TEXT,
    target_number REAL,
    doses_administered REAL,
    coverage_pct REAL,
    FOREIGN KEY (country_code) REFERENCES dim_countries(country_code),
    FOREIGN KEY (antigen_code) REFERENCES dim_antigens(antigen_code)
);

-- ----------------------------------------------------------------------------
-- Fact 2: fact_incidence
-- Stores disease incidence rates per specified population denominator
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS fact_incidence;
CREATE TABLE fact_incidence (
    incidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_code VARCHAR(3) NOT NULL,
    year INTEGER NOT NULL,
    disease_code VARCHAR(20) NOT NULL,
    denominator_unit VARCHAR(100),
    incidence_rate REAL,
    FOREIGN KEY (country_code) REFERENCES dim_countries(country_code),
    FOREIGN KEY (disease_code) REFERENCES dim_diseases(disease_code)
);

-- ----------------------------------------------------------------------------
-- Fact 3: fact_reported_cases
-- Stores raw reported disease cases by year and region
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS fact_reported_cases;
CREATE TABLE fact_reported_cases (
    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_code VARCHAR(3) NOT NULL,
    year INTEGER NOT NULL,
    disease_code VARCHAR(20) NOT NULL,
    reported_cases INTEGER NOT NULL,
    FOREIGN KEY (country_code) REFERENCES dim_countries(country_code),
    FOREIGN KEY (disease_code) REFERENCES dim_diseases(disease_code)
);

-- ----------------------------------------------------------------------------
-- Fact 4: fact_vaccine_intro
-- Tracks year of vaccine introduction into national programs
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS fact_vaccine_intro;
CREATE TABLE fact_vaccine_intro (
    intro_id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_code VARCHAR(3) NOT NULL,
    year INTEGER NOT NULL,
    vaccine_description VARCHAR(150) NOT NULL,
    intro_status VARCHAR(20) NOT NULL,
    FOREIGN KEY (country_code) REFERENCES dim_countries(country_code)
);

-- ----------------------------------------------------------------------------
-- Fact 5: fact_vaccine_schedule
-- Captures target population, age administered, and schedule rounds
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS fact_vaccine_schedule;
CREATE TABLE fact_vaccine_schedule (
    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_code VARCHAR(3) NOT NULL,
    year INTEGER NOT NULL,
    vaccine_code VARCHAR(20) NOT NULL,
    vaccine_description VARCHAR(150) NOT NULL,
    schedule_rounds VARCHAR(50),
    target_pop VARCHAR(100),
    target_pop_description TEXT,
    geo_area VARCHAR(50),
    age_administered VARCHAR(50),
    source_comment TEXT,
    FOREIGN KEY (country_code) REFERENCES dim_countries(country_code)
);

-- ----------------------------------------------------------------------------
-- Fact 6: fact_socioeconomic
-- Tracks socioeconomic breakdowns (Gender, Urban/Rural, Education)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS fact_socioeconomic;
CREATE TABLE fact_socioeconomic (
    socio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_code VARCHAR(3) NOT NULL,
    year INTEGER NOT NULL,
    dimension VARCHAR(50) NOT NULL,
    subgroup VARCHAR(50) NOT NULL,
    coverage_pct REAL,
    dropout_rate_pct REAL,
    population_density_sqkm REAL,
    vaccination_strategy VARCHAR(100),
    seasonal_peak_quarter VARCHAR(10),
    FOREIGN KEY (country_code) REFERENCES dim_countries(country_code)
);

-- ----------------------------------------------------------------------------
-- Indexes for Optimization
-- ----------------------------------------------------------------------------
CREATE INDEX idx_cov_country_yr ON fact_coverage(country_code, year);
CREATE INDEX idx_cov_antigen ON fact_coverage(antigen_code);
CREATE INDEX idx_inc_country_yr ON fact_incidence(country_code, year);
CREATE INDEX idx_inc_disease ON fact_incidence(disease_code);
CREATE INDEX idx_cases_country_yr ON fact_reported_cases(country_code, year);
CREATE INDEX idx_socio_dim_subgroup ON fact_socioeconomic(dimension, subgroup);

-- ----------------------------------------------------------------------------
-- Views for Reporting & Power BI Integration
-- ----------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_coverage_incidence_joined;
CREATE VIEW vw_coverage_incidence_joined AS
SELECT 
    c.country_code,
    c.country_name,
    c.who_region,
    c.income_group,
    fc.year,
    fc.antigen_code,
    da.antigen_description,
    da.target_disease_code,
    fc.coverage_pct,
    fi.incidence_rate,
    frc.reported_cases
FROM fact_coverage fc
JOIN dim_countries c ON fc.country_code = c.country_code
JOIN dim_antigens da ON fc.antigen_code = da.antigen_code
LEFT JOIN fact_incidence fi ON fc.country_code = fi.country_code 
    AND fc.year = fi.year 
    AND da.target_disease_code = fi.disease_code
LEFT JOIN fact_reported_cases frc ON fc.country_code = frc.country_code 
    AND fc.year = frc.year 
    AND da.target_disease_code = frc.disease_code;
