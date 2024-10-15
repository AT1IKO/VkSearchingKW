import psycopg2

def connect_to_db(db_name, user, password, host, port):
    return psycopg2.connect(
        dbname=db_name,
        user=user,
        password=password,
        host=host,
        port=port
    )

def get_keywords_by_category(conn, category):
    cursor = conn.cursor()
    cursor.execute("SELECT keyword FROM keywords WHERE category = %s", (category,))
    keywords = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return keywords

