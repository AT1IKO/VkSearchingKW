import psycopg2
from psycopg2 import sql
from other_fun import get_group_id_by_screen_name

def connect_db():
    """Подключение к базе данных"""
    conn = psycopg2.connect(
        dbname='SearchingVK',
        user='postgres',
        password='111123',
        host='localhost',
        port='5432'
    )
    return conn

def insert_post(group_id, post_id, content, created_at, author_id, likes, reposts, views):
    """
    Вставляет запись поста в базу данных, проверяя на дубликаты по уникальному record_id
    :param group_id: ID группы
    :param post_id: ID поста
    :param content: текст поста
    :param created_at: дата создания поста
    :param author_id: ID автора поста
    :param likes: количество лайков
    :param reposts: количество репостов
    :param views: количество просмотров
    :return: None
    """
    conn = connect_db()
    cur = conn.cursor()

    # Формирование record_id
    record_id = str(group_id) + str(post_id)

    # Проверка на дубликат
    cur.execute("SELECT * FROM posts WHERE \"ID записи\" = %s", (record_id,))
    if cur.fetchone() is None:
        cur.execute("""
            INSERT INTO posts ("ID записи", "ID группы", "ID поста", content, created_at, author_id, likes, reposts, views)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (record_id, group_id, post_id, content, created_at, author_id, likes, reposts, views))

    conn.commit()
    cur.close()
    conn.close()

def insert_comment(group_id, post_id, comment_id, content, created_at, author_id, likes):
    """
    Вставляет запись комментария в базу данных, проверяя на дубликаты по уникальному record_id
    :param group_id: ID группы
    :param post_id: ID поста, к которому относится комментарий
    :param comment_id: ID комментария
    :param content: текст комментария
    :param created_at: дата создания комментария
    :param author_id: ID автора комментария
    :param likes: количество лайков
    :return: None
    """
    conn = connect_db()
    cur = conn.cursor()

    # Формирование record_id
    record_id = str(group_id) + str(post_id) + str(comment_id)

    # Проверка на дубликат
    cur.execute("SELECT * FROM comments WHERE \"ID записи\" = %s", (record_id,))
    if cur.fetchone() is None:
        cur.execute("""
            INSERT INTO comments ("ID записи", "ID группы", "ID поста", "ID комментария", content, created_at, author_id, likes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (record_id, group_id, post_id, comment_id, content, created_at, author_id, likes))

    conn.commit()
    cur.close()
    conn.close()

def get_groups_by_category(categories):
    """
    Получает группы из базы данных по заданным категориям.
    :param categories: список категорий, для которых нужно загрузить группы.
    :return: список групп
    """
    conn = connect_db()
    cur = conn.cursor()

    query = "SELECT group_name, group_url FROM groups"
    if categories:
        query += " WHERE category IN %s"
        cur.execute(query, (tuple(categories),))
    else:
        cur.execute(query)

    groups = cur.fetchall()
    cur.close()
    conn.close()

    return groups

def get_keywords_by_category(categories):
    """
    Получает ключевые слова из базы данных по заданным категориям.
    :param categories: список категорий, для которых нужно загрузить ключевые слова
    :return: список ключевых слов
    """
    conn = connect_db()
    cur = conn.cursor()

    # Если категории заданы, фильтруем ключевые слова по категориям
    query = "SELECT keyword FROM keywords"
    if categories:
        query += " WHERE category IN %s"
        cur.execute(query, (tuple(categories),))
    else:
        cur.execute(query)

    keywords = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()

    return keywords

def add_groups_to_db(vk_token, group_screen_names, category):
    """
    Добавляет группы в базу данных по их коротким именам.
    :param vk_token: VK API токен
    :param group_screen_names: список коротких имен групп
    :param category: категория, которую нужно присвоить этим группам
    :return: None
    """
    conn = connect_db()
    cur = conn.cursor()

    for group_screen_name in group_screen_names:
        # Получаем числовой ID группы
        group_id = get_group_id_by_screen_name(vk_token, group_screen_name)

        # Вставляем данные в таблицу groups
        cur.execute("""
            INSERT INTO groups ("ID группы", group_name, category)
            VALUES (%s, %s, %s)
            ON CONFLICT ("ID группы") DO NOTHING;
        """, (group_id, group_screen_name, category))

    conn.commit()
    cur.close()
    conn.close()

def add_keywords_to_db(keywords, category):
    """
    Добавляет ключевые слова в базу данных с указанием их категории.
    :param keywords: список ключевых слов
    :param category: категория, которую нужно присвоить этим ключевым словам
    :return: None
    """
    conn = connect_db()  # Подключение к базе данных
    cur = conn.cursor()

    for keyword in keywords:
        # Вставляем данные в таблицу keywords
        cur.execute("""
            INSERT INTO keywords (keyword, category)
            VALUES (%s, %s)
            ON CONFLICT (keyword) DO NOTHING;
        """, (keyword, category))

    conn.commit()
    cur.close()
    conn.close()

