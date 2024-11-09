import pyodbc

SERVER = 'localhost\\SQLEXPRESS'  # Use localhost or IP address
DATABASE = 'vc_test'
DRIVER = 'ODBC Driver 18 for SQL Server'

# Connection string with Windows Authentication
connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;Encrypt=no;TrustServerCertificate=yes'

conn = None

try:
    conn = pyodbc.connect(connection_string)
    print("Connection successful!")
except Exception as e:
    print(f"Error connecting to the database: {e}")
finally:
    if conn:
        conn.close()
