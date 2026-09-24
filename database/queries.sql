-- ============================================================================
-- SQL Analytical Query Suite: Vaccination Data Analysis
-- Database: SQLite3 (vaccination_db.sqlite)
-- Answering 30 Analytical Questions: Easy (1-10), Medium (1-10), Scenario (1-10)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- EASY LEVEL QUESTIONS
-- ----------------------------------------------------------------------------

-- Q1. How do vaccination rates correlate with a decrease in disease incidence?
SELECT 
    da.antigen_code,
    da.antigen_description,
    ROUND(AVG(fc.coverage_pct), 2) AS avg_coverage_pct,
    ROUND(AVG(fi.incidence_rate), 2) AS avg_incidence_rate
FROM fact_coverage fc
JOIN dim_antigens da ON fc.antigen_code = da.antigen_code
JOIN fact_incidence fi ON fc.country_code = fi.country_code 
    AND fc.year = fi.year 
    AND da.target_disease_code = fi.disease_code
GROUP BY da.antigen_code, da.antigen_description
ORDER BY avg_coverage_pct DESC;

-- Q2. What is the drop-off rate between 1st dose and subsequent doses?
SELECT 
    fc1.country_code,
    c.country_name,
    fc1.year,
    ROUND(fc1.coverage_pct, 2) AS mcv1_coverage_pct,
    ROUND(fc2.coverage_pct, 2) AS mcv2_coverage_pct,
    ROUND(fc1.coverage_pct - fc2.coverage_pct, 2) AS dropout_rate_pct
FROM fact_coverage fc1
JOIN fact_coverage fc2 ON fc1.country_code = fc2.country_code AND fc1.year = fc2.year
JOIN dim_countries c ON fc1.country_code = c.country_code
WHERE fc1.antigen_code = 'MCV1' AND fc2.antigen_code = 'MCV2'
ORDER BY dropout_rate_pct DESC
LIMIT 10;

-- Q3. Are vaccination rates different between genders?
SELECT 
    subgroup AS gender,
    ROUND(AVG(coverage_pct), 2) AS avg_coverage_pct,
    ROUND(AVG(dropout_rate_pct), 2) AS avg_dropout_rate_pct
FROM fact_socioeconomic
WHERE dimension = 'Gender'
GROUP BY subgroup;

-- Q4. How does education level impact vaccination rates?
SELECT 
    subgroup AS education_level,
    ROUND(AVG(coverage_pct), 2) AS avg_coverage_pct,
    ROUND(AVG(dropout_rate_pct), 2) AS avg_dropout_rate_pct
FROM fact_socioeconomic
WHERE dimension = 'Education_Level'
GROUP BY subgroup
ORDER BY avg_coverage_pct DESC;

-- Q5. What is the urban vs. rural vaccination rate difference?
SELECT 
    subgroup AS geographic_setting,
    ROUND(AVG(coverage_pct), 2) AS avg_coverage_pct,
    ROUND(AVG(dropout_rate_pct), 2) AS avg_dropout_rate_pct
FROM fact_socioeconomic
WHERE dimension = 'Urban_Rural'
GROUP BY subgroup;

-- Q6. Has the rate of booster dose uptake increased over time?
SELECT 
    year,
    antigen_code,
    ROUND(AVG(coverage_pct), 2) AS avg_booster_coverage_pct
FROM fact_coverage
WHERE antigen_code IN ('MCV2', 'DTP3', 'HPV')
GROUP BY year, antigen_code
ORDER BY antigen_code, year;

-- Q7. Is there a seasonal pattern in vaccination uptake?
SELECT 
    seasonal_peak_quarter,
    c.who_region,
    COUNT(*) AS records_count,
    ROUND(AVG(coverage_pct), 2) AS avg_coverage_pct
FROM fact_socioeconomic fs
JOIN dim_countries c ON fs.country_code = c.country_code
GROUP BY seasonal_peak_quarter, c.who_region
ORDER BY c.who_region, avg_coverage_pct DESC;

-- Q8. How does population density relate to vaccination coverage?
SELECT 
    c.country_name,
    c.population_density_sqkm,
    ROUND(AVG(fc.coverage_pct), 2) AS avg_coverage_pct
FROM dim_countries c
JOIN fact_coverage fc ON c.country_code = fc.country_code
GROUP BY c.country_name, c.population_density_sqkm
ORDER BY c.population_density_sqkm DESC;

-- Q9. Regional breakdown of vaccination coverage vs disease incidence
SELECT 
    c.who_region,
    ROUND(AVG(fc.coverage_pct), 2) AS avg_coverage_pct,
    ROUND(AVG(fi.incidence_rate), 2) AS avg_incidence_rate
FROM dim_countries c
JOIN fact_coverage fc ON c.country_code = fc.country_code
JOIN fact_incidence fi ON c.country_code = fi.country_code AND fc.year = fi.year
GROUP BY c.who_region
ORDER BY avg_coverage_pct DESC;

-- Q10. Which regions have high disease incidence despite high vaccination rates?
SELECT 
    c.who_region,
    c.country_name,
    ROUND(AVG(fc.coverage_pct), 2) AS avg_coverage_pct,
    ROUND(AVG(fi.incidence_rate), 2) AS avg_incidence_rate
FROM dim_countries c
JOIN fact_coverage fc ON c.country_code = fc.country_code
JOIN fact_incidence fi ON c.country_code = fi.country_code AND fc.year = fi.year
GROUP BY c.who_region, c.country_name
HAVING avg_coverage_pct > 75.0 AND avg_incidence_rate > 50.0
ORDER BY avg_incidence_rate DESC;

-- ----------------------------------------------------------------------------
-- MEDIUM LEVEL QUESTIONS
-- ----------------------------------------------------------------------------

-- Q1. Is there a correlation between vaccine introduction and a decrease in disease cases?
SELECT 
    fvi.vaccine_description,
    fvi.intro_status,
    ROUND(AVG(frc.reported_cases), 0) AS avg_reported_cases
FROM fact_vaccine_intro fvi
JOIN dim_antigens da ON fvi.vaccine_description LIKE '%' || da.antigen_code || '%' OR da.antigen_description LIKE '%' || fvi.vaccine_description || '%'
JOIN fact_reported_cases frc ON fvi.country_code = frc.country_code AND fvi.year = frc.year AND da.target_disease_code = frc.disease_code
GROUP BY fvi.vaccine_description, fvi.intro_status
ORDER BY fvi.vaccine_description, avg_reported_cases DESC;

-- Q2. What is the trend in disease cases before and after vaccination campaigns?
SELECT 
    fvi.country_code,
    c.country_name,
    fvi.vaccine_description,
    fvi.year,
    fvi.intro_status,
    SUM(frc.reported_cases) AS total_cases
FROM fact_vaccine_intro fvi
JOIN dim_countries c ON fvi.country_code = c.country_code
JOIN fact_reported_cases frc ON fvi.country_code = frc.country_code AND fvi.year = frc.year
WHERE fvi.vaccine_description LIKE '%Rotavirus%'
GROUP BY fvi.country_code, c.country_name, fvi.vaccine_description, fvi.year, fvi.intro_status
ORDER BY c.country_name, fvi.year;

-- Q3. Which diseases have shown the most significant reduction in cases due to vaccination?
SELECT 
    dd.disease_code,
    dd.disease_description,
    MAX(frc.reported_cases) AS peak_cases,
    MIN(frc.reported_cases) AS recent_min_cases,
    ROUND(((MAX(frc.reported_cases) - MIN(frc.reported_cases)) * 100.0 / MAX(frc.reported_cases)), 2) AS pct_reduction
FROM fact_reported_cases frc
JOIN dim_diseases dd ON frc.disease_code = dd.disease_code
GROUP BY dd.disease_code, dd.disease_description
ORDER BY pct_reduction DESC;

-- Q4. What percentage of the target population has been covered by each vaccine?
SELECT 
    da.antigen_code,
    da.antigen_description,
    ROUND(SUM(fc.doses_administered) * 100.0 / NULLIF(SUM(fc.target_number), 0), 2) AS global_target_coverage_pct
FROM fact_coverage fc
JOIN dim_antigens da ON fc.antigen_code = da.antigen_code
GROUP BY da.antigen_code, da.antigen_description
ORDER BY global_target_coverage_pct DESC;

-- Q5. How does the vaccination schedule (e.g., booster doses) impact target population coverage?
SELECT 
    fvs.schedule_rounds,
    ROUND(AVG(fc.coverage_pct), 2) AS avg_coverage_pct
FROM fact_vaccine_schedule fvs
JOIN fact_coverage fc ON fvs.country_code = fc.country_code AND fvs.year = fc.year AND fvs.vaccine_code = fc.antigen_code
GROUP BY fvs.schedule_rounds
ORDER BY avg_coverage_pct DESC;

-- Q6. Are there significant disparities in vaccine introduction timelines across WHO regions?
SELECT 
    c.who_region,
    fvi.vaccine_description,
    MIN(fvi.year) AS first_intro_year,
    MAX(CASE WHEN fvi.intro_status = 'Yes' THEN fvi.year END) AS full_intro_year
FROM fact_vaccine_intro fvi
JOIN dim_countries c ON fvi.country_code = c.country_code
WHERE fvi.intro_status IN ('Partial', 'Yes')
GROUP BY c.who_region, fvi.vaccine_description
ORDER BY fvi.vaccine_description, first_intro_year;

-- Q7. How does vaccine coverage correlate with disease reduction for specific antigens?
SELECT 
    da.antigen_code,
    ROUND(AVG(fc.coverage_pct), 2) AS avg_coverage_pct,
    ROUND(AVG(fi.incidence_rate), 2) AS avg_incidence_rate
FROM fact_coverage fc
JOIN dim_antigens da ON fc.antigen_code = da.antigen_code
JOIN fact_incidence fi ON fc.country_code = fi.country_code AND fc.year = fi.year AND da.target_disease_code = fi.disease_code
GROUP BY da.antigen_code
ORDER BY avg_coverage_pct DESC;

-- Q8. Are there specific regions or countries with low coverage despite high availability of vaccines?
SELECT 
    c.who_region,
    c.country_name,
    ROUND(AVG(fc.coverage_pct), 2) AS avg_coverage_pct,
    COUNT(CASE WHEN fvi.intro_status = 'Yes' THEN 1 END) AS vaccines_available
FROM dim_countries c
JOIN fact_coverage fc ON c.country_code = fc.country_code
JOIN fact_vaccine_intro fvi ON c.country_code = fvi.country_code AND fc.year = fvi.year
GROUP BY c.who_region, c.country_name
HAVING avg_coverage_pct < 70.0 AND vaccines_available > 5
ORDER BY avg_coverage_pct ASC;

-- Q9. What are the gaps in coverage for vaccines targeting high-priority diseases (e.g., TB, Hepatitis B)?
SELECT 
    da.antigen_code,
    da.antigen_description,
    ROUND(AVG(fc.coverage_pct), 2) AS avg_coverage_pct,
    ROUND(100.0 - AVG(fc.coverage_pct), 2) AS global_coverage_gap_pct
FROM dim_antigens da
JOIN fact_coverage fc ON da.antigen_code = fc.antigen_code
WHERE da.target_disease_code IN ('TUBERCULOSIS', 'HEPB', 'MEASLES', 'POLIO')
GROUP BY da.antigen_code, da.antigen_description
ORDER BY global_coverage_gap_pct DESC;

-- Q10. Are certain diseases more prevalent in specific geographic areas?
SELECT 
    c.who_region,
    dd.disease_description,
    ROUND(AVG(fi.incidence_rate), 2) AS avg_incidence_rate,
    SUM(frc.reported_cases) AS total_cases
FROM dim_countries c
JOIN fact_incidence fi ON c.country_code = fi.country_code
JOIN fact_reported_cases frc ON fi.country_code = frc.country_code AND fi.year = frc.year AND fi.disease_code = frc.disease_code
JOIN dim_diseases dd ON fi.disease_code = dd.disease_code
GROUP BY c.who_region, dd.disease_description
ORDER BY avg_incidence_rate DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- SCENARIO BASED QUESTIONS
-- ----------------------------------------------------------------------------

-- S1. Identify regions/countries with low vaccination coverage for targeted resource allocation
SELECT 
    c.who_region,
    c.country_name,
    ROUND(AVG(fc.coverage_pct), 2) AS avg_coverage_pct,
    CASE 
        WHEN AVG(fc.coverage_pct) < 65.0 THEN 'High Priority Resource Intervention'
        WHEN AVG(fc.coverage_pct) < 80.0 THEN 'Moderate Priority Outreach'
        ELSE 'Sustained Maintenance'
    END AS resource_allocation_priority
FROM dim_countries c
JOIN fact_coverage fc ON c.country_code = fc.country_code
GROUP BY c.who_region, c.country_name
ORDER BY avg_coverage_pct ASC;

-- S2. Evaluate the effectiveness of a measles vaccination campaign launched 5 years ago (e.g. 2018-2024 vs pre-2018)
SELECT 
    c.country_name,
    CASE WHEN fc.year >= 2019 THEN 'Post-Campaign (2019-2024)' ELSE 'Pre-Campaign (2010-2018)' END AS campaign_period,
    ROUND(AVG(fc.coverage_pct), 2) AS avg_measles_coverage,
    ROUND(AVG(fi.incidence_rate), 2) AS avg_measles_incidence,
    SUM(frc.reported_cases) AS total_measles_cases
FROM fact_coverage fc
JOIN dim_countries c ON fc.country_code = c.country_code
JOIN dim_antigens da ON fc.antigen_code = da.antigen_code
JOIN fact_incidence fi ON fc.country_code = fi.country_code AND fc.year = fi.year AND da.target_disease_code = fi.disease_code
JOIN fact_reported_cases frc ON fc.country_code = frc.country_code AND fc.year = frc.year AND da.target_disease_code = frc.disease_code
WHERE da.antigen_code IN ('MCV1', 'MCV2')
GROUP BY c.country_name, campaign_period
ORDER BY c.country_name, campaign_period;

-- S3. Estimate vaccine demand for upcoming year based on target population trend
SELECT 
    c.country_name,
    da.antigen_code,
    ROUND(AVG(fc.target_number), 0) AS current_avg_target,
    ROUND(AVG(fc.target_number) * 1.025, 0) AS forecast_upcoming_demand_doses
FROM fact_coverage fc
JOIN dim_countries c ON fc.country_code = c.country_code
JOIN dim_antigens da ON fc.antigen_code = da.antigen_code
WHERE fc.year = 2024
GROUP BY c.country_name, da.antigen_code
ORDER BY forecast_upcoming_demand_doses DESC
LIMIT 10;

-- S4. Detect sudden outbreak of influenza in a specific region needing vaccine ramp up
SELECT 
    c.who_region,
    c.country_name,
    frc.year,
    frc.reported_cases AS influenza_cases,
    fi.incidence_rate
FROM fact_reported_cases frc
JOIN dim_countries c ON frc.country_code = c.country_code
JOIN fact_incidence fi ON frc.country_code = fi.country_code AND frc.year = fi.year AND frc.disease_code = fi.disease_code
WHERE frc.disease_code = 'INFLUENZA' AND frc.reported_cases > 1000
ORDER BY frc.reported_cases DESC;

-- S5. Explore incidence rates of polio in populations with low/no coverage
SELECT 
    c.country_name,
    fc.year,
    fc.coverage_pct AS polio_coverage_pct,
    fi.incidence_rate AS polio_incidence_rate,
    frc.reported_cases AS polio_cases
FROM fact_coverage fc
JOIN dim_countries c ON fc.country_code = c.country_code
JOIN fact_incidence fi ON fc.country_code = fi.country_code AND fc.year = fi.year AND fi.disease_code = 'POLIO'
JOIN fact_reported_cases frc ON fc.country_code = frc.country_code AND fc.year = frc.year AND frc.disease_code = 'POLIO'
WHERE fc.antigen_code = 'POL3' AND fc.coverage_pct < 70.0
ORDER BY fc.coverage_pct ASC;

-- S6. Track global progress toward WHO target of 95% vaccination coverage for measles by 2030
SELECT 
    fc.year,
    ROUND(AVG(fc.coverage_pct), 2) AS global_avg_mcv1_coverage,
    95.0 AS who_2030_target_pct,
    ROUND(95.0 - AVG(fc.coverage_pct), 2) AS gap_to_target_pct
FROM fact_coverage fc
WHERE fc.antigen_code = 'MCV1'
GROUP BY fc.year
ORDER BY fc.year;

-- S7. High-risk population target allocation (Infants < 1 yr vs Elderly)
SELECT 
    fvs.target_pop,
    fvs.age_administered,
    COUNT(DISTINCT fvs.vaccine_code) AS vaccines_count,
    ROUND(AVG(fc.coverage_pct), 2) AS avg_group_coverage_pct
FROM fact_vaccine_schedule fvs
JOIN fact_coverage fc ON fvs.country_code = fc.country_code AND fvs.year = fc.year AND fvs.vaccine_code = fc.antigen_code
GROUP BY fvs.target_pop, fvs.age_administered
ORDER BY avg_group_coverage_pct ASC;

-- S8. Socioeconomic disparities detection across dimensions
SELECT 
    dimension,
    subgroup,
    ROUND(AVG(coverage_pct), 2) AS avg_coverage_pct,
    ROUND(AVG(dropout_rate_pct), 2) AS avg_dropout_pct
FROM fact_socioeconomic
GROUP BY dimension, subgroup
ORDER BY dimension, avg_coverage_pct ASC;

-- S9. Seasonal variation in vaccination rates across WHO regions
SELECT 
    c.who_region,
    fs.seasonal_peak_quarter,
    ROUND(AVG(fs.coverage_pct), 2) AS avg_coverage_pct
FROM fact_socioeconomic fs
JOIN dim_countries c ON fs.country_code = c.country_code
GROUP BY c.who_region, fs.seasonal_peak_quarter
ORDER BY c.who_region, avg_coverage_pct DESC;

-- S10. Evaluate effectiveness of vaccination strategies (Door-to-Door vs Centralized Clinic vs Mobile Unit)
SELECT 
    vaccination_strategy,
    ROUND(AVG(coverage_pct), 2) AS avg_coverage_pct,
    ROUND(AVG(dropout_rate_pct), 2) AS avg_dropout_rate_pct
FROM fact_socioeconomic
GROUP BY vaccination_strategy
ORDER BY avg_coverage_pct DESC;
