// ============================================================================
// Power Query M ETL Script: Automated Ingestion and Transformation
// Purpose: Load cleaned data into Power BI from CSV files or SQLite database
// ============================================================================

// Query 1: dim_countries
let
    Source = Csv.Document(File.Contents("data/cleaned/coverage_data_clean.csv"),[Delimiter=",", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    SelectColumns = Table.SelectColumns(PromotedHeaders, {"Code"}),
    RemovedDuplicates = Table.Distinct(SelectColumns),
    RenamedColumns = Table.RenameColumns(RemovedDuplicates,{{"Code", "country_code"}})
in
    RenamedColumns

// Query 2: fact_coverage
let
    Source = Csv.Document(File.Contents("data/cleaned/coverage_data_clean.csv"),[Delimiter=",", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"Year", Int64.Type}, 
        {"Coverage_Pct", type number}, 
        {"Target_number", type number}, 
        {"Dodge", type number}
    }),
    RenameCols = Table.RenameColumns(ChangeTypes,{
        {"Code", "country_code"},
        {"Year", "year"},
        {"Antigen", "antigen_code"},
        {"Coverage_Category", "coverage_category"},
        {"Coverage_Category_Description", "coverage_category_description"},
        {"Target_number", "target_number"},
        {"Dodge", "doses_administered"},
        {"Coverage_Pct", "coverage_pct"}
    })
in
    RenameCols

// Query 3: fact_incidence
let
    Source = Csv.Document(File.Contents("data/cleaned/incidence_rate_clean.csv"),[Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"Year", Int64.Type}, 
        {"Incidence_rate", type number}
    }),
    RenameCols = Table.RenameColumns(ChangeTypes,{
        {"Code", "country_code"},
        {"Year", "year"},
        {"Disease", "disease_code"},
        {"Denominator", "denominator_unit"},
        {"Incidence_rate", "incidence_rate"}
    })
in
    RenameCols

// Query 4: fact_reported_cases
let
    Source = Csv.Document(File.Contents("data/cleaned/reported_cases_clean.csv"),[Delimiter=",", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"Year", Int64.Type}, 
        {"Cases", Int64.Type}
    }),
    RenameCols = Table.RenameColumns(ChangeTypes,{
        {"Code", "country_code"},
        {"Year", "year"},
        {"Disease", "disease_code"},
        {"Cases", "reported_cases"}
    })
in
    RenameCols

// Query 5: fact_socioeconomic
let
    Source = Csv.Document(File.Contents("data/cleaned/socioeconomic_metrics_clean.csv"),[Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"Year", Int64.Type}, 
        {"Coverage_Pct", type number},
        {"Dropout_Rate_Pct", type number},
        {"Population_Density_sqkm", type number}
    }),
    RenameCols = Table.RenameColumns(ChangeTypes,{
        {"Code", "country_code"},
        {"Year", "year"},
        {"Dimension", "dimension"},
        {"Subgroup", "subgroup"},
        {"Coverage_Pct", "coverage_pct"},
        {"Dropout_Rate_Pct", "dropout_rate_pct"},
        {"Population_Density_sqkm", "population_density_sqkm"},
        {"Vaccination_Strategy", "vaccination_strategy"},
        {"Seasonal_Peak_Quarter", "seasonal_peak_quarter"}
    })
in
    RenameCols
