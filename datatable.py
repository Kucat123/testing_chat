import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('logs.db')
cursor = conn.cursor()

# Retrieve the names of all tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Iterate over each table and fetch its data
for table_name in tables:
    table_name = table_name[0]  # Extract table name from tuple
    print(f"Data from table: {table_name}")
    
    # Fetch all data from the current table
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Fetch column names for the current table
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]

    # Print column names
    print(" | ".join(column_names))

    # Print rows of data
    for row in rows:
        print(row)

    print("\n" + "-"*50 + "\n")
conn.close()
