import sqlite3

conn = sqlite3.connect("ecom.db")
cursor = conn.cursor()

print("Tables in ecom.db:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())

print("\nCustomer count:")
cursor.execute("SELECT COUNT(*) FROM customers;")
print(cursor.fetchone())

conn.close()

