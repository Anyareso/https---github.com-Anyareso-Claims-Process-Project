import pyodbc

SERVER = 'Merlin\\SQLEXPRESS'
DATABASE = 'vc_test'
DRIVER = 'ODBC Driver 18 for SQL Server'
UID = 'USER-PC'   # Remove this line if using Trusted_Connection
PWD = 'password'   # Remove this line if using Trusted_Connection

# Connection string
connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;Encrypt=no;TrustServerCertificate=yes'

conn = None  # Ensure conn is always defined

try:
    conn = pyodbc.connect(connection_string)
    print("Connection successful!")
except Exception as e:
    print(f"Error connecting to the database: {e}")
finally:
    if conn:
        conn.close()
