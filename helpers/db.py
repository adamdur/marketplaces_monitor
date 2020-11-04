def insert_post(db, data):
    cursor = db.cursor()
    insert_query = ("INSERT INTO posts (bot, type, price, marketplace, created_at, content, is_lifetime) VALUES (%s, %s, %s, %s, %s, %s, %s)")

    cursor.execute(insert_query, data)
    post = cursor.lastrowid

    db.commit()
    return post
