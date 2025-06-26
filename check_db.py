# In: check_db.py

import duckdb
import os

DB_FILE = "asset_universe.duckdb"

print(f"--- Checking for database file: '{DB_FILE}' ---")

# Check if the file exists in the current directory
if not os.path.exists(DB_FILE):
    print(
        f"❌ FAILURE: The database file '{DB_FILE}' does not exist in this directory."
    )
    print("   Please run 'python cli.py' first to create it.")
else:
    print(f"✅ SUCCESS: Found the database file '{DB_FILE}'.")
    try:
        print("\n--- Querying the 'candidates' table ---")
        con = duckdb.connect(database=DB_FILE, read_only=True)
        # Use fetch_df() which is an alias for fetchdf() in newer versions
        df = con.execute("SELECT * FROM candidates;").fetch_df()
        con.close()

        if df.empty:
            print("❌ FAILURE: The 'candidates' table is empty.")
        else:
            print("✅ SUCCESS: The 'candidates' table contains data.")
            print("\n--- Table Contents ---")
            print(df)

    except Exception as e:
        print(f"\n❌ FAILURE: An error occurred while reading the database: {e}")
