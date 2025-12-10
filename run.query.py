import sqlite3

def run_query():
    # Connect to the existing SQLite database
    conn = sqlite3.connect("ecom.db")
    cursor = conn.cursor()

    # Read SQL from file
    with open("queries.sql", "r", encoding="utf-8") as f:
        sql_query = f.read().strip()

    # Execute the SQL query
    cursor.execute(sql_query)

    rows = cursor.fetchall()

    print("Query result:")
    for row in rows:
        print(row)

    conn.close()

if __name__ == "__main__":
    run_query()
