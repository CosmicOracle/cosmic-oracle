import psycopg2
from app.core.config import settings

try:
    # Connect to the database
    conn = psycopg2.connect(
        dbname="cosmic_oracle",
        user="cosmic-master",
        password="CrazyLoserStalker1991$",
        host="localhost",
        port=5432,
        options=f"-c search_path=cosmic_schema,public"
    )
    print("Successfully connected to the database!")
    
    # Create a cursor
    cur = conn.cursor()
    
    # Execute a simple query
    cur.execute("SELECT 1")
    result = cur.fetchone()
    print(f"Test query result: {result}")
    
    # Close the cursor and connection
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error connecting to the database: {e}")
