import os
import sqlite3
import pandas as pd

def run_sql_analysis():
    db_path = os.path.join("database", "vaccination_db.sqlite")
    queries_path = os.path.join("database", "queries.sql")
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file {db_path} not found!")
    if not os.path.exists(queries_path):
        raise FileNotFoundError(f"Queries file {queries_path} not found!")
        
    conn = sqlite3.connect(db_path)
    
    with open(queries_path, "r", encoding="utf-8") as f:
        sql_content = f.read()
        
    raw_queries = [q.strip() for q in sql_content.split(";") if q.strip()]
    
    print("=" * 80)
    print(f"EXECUTING {len(raw_queries)} SQL ANALYTICAL QUERIES AGAINST {db_path}")
    print("=" * 80 + "\n")
    
    successful_execs = 0
    for idx, query in enumerate(raw_queries, 1):
        header = f"Query {idx}"
        lines = query.splitlines()
        for line in lines:
            if line.strip().startswith("--"):
                header = line.strip("--").strip()
                break
                
        try:
            df_res = pd.read_sql_query(query, conn)
            successful_execs += 1
            print(f"[{idx:02d}/{len(raw_queries):02d}] {header}")
            print("-" * 70)
            if not df_res.empty:
                print(df_res.head(5).to_string(index=False))
            else:
                print("(No records returned)")
            print("\n" + "=" * 80 + "\n")
        except Exception as e:
            print(f"[{idx:02d}/{len(raw_queries):02d}] ERROR: {header}")
            print(f"       Message: {e}\n")
            
    conn.close()
    print(f"ALL QUERIES EXECUTED! {successful_execs}/{len(raw_queries)} queries completed successfully.")

if __name__ == "__main__":
    run_sql_analysis()
