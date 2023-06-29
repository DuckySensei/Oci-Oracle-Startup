import cx_Oracle

# Set up connection details
username = "--"
password = "--"
host = "--"
port = "--"
service_name = "--"

# Construct the connection string
dsn = cx_Oracle.makedsn(host, port, service_name=service_name)

# Establish the connection
connection = cx_Oracle.connect(username, password, dsn)

# Create a cursor to execute SQL statements
cursor = connection.cursor()

# Execute a sample query
cursor.execute("SELECT * FROM your_table")

# Fetch and print the results
rows = cursor.fetchall()
for row in rows:
      print(row)

# Close the cursor and the connection
cursor.close()
connection.close()
