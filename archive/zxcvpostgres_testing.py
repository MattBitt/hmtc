import psycopg2

conn = psycopg2.connect(
    database="testing",
    user="postgres",
    host="192.168.0.202",
    password="postgres",
    port=5432,
)

cur = conn.cursor()
cur.execute(
    """CREATE TABLE datacamp_courses(
            course_id SERIAL PRIMARY KEY,
            course_name VARCHAR (50) UNIQUE NOT NULL,
            course_instructor VARCHAR (100) NOT NULL,
            topic VARCHAR (20) NOT NULL);
            """
)
# Make the changes to the database persistent
conn.commit()
# Close cursor and communication with the database
cur.close()
conn.close()
