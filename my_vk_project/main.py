import time
from vk_api_functions import connect_to_vk, get_last_posts, get_group_id, get_comments
from db_functions import connect_to_db, get_keywords_by_category

VK_API_TOKEN = '00ba214000ba214000ba21402a039ae22f000ba00ba214067b75a55842494769f307399'
GROUP_NAME = 'kino_kaif'
DB_CONFIG = {
    'db_name': 'SearchingVK',
    'user': 'postgres',
    'password': '111123',
    'host': 'localhost',
    'port': '5432'
}

def main():
    # Засекаем общее время выполнения программы
    total_start_time = time.time()

    # Подключение к VK API
    vk = connect_to_vk(VK_API_TOKEN)

    # Получение числового ID группы
    group_id = get_group_id(vk, GROUP_NAME)
    print(f"Числовой ID группы: {group_id}")

    # Подключение к базе данных
    conn = connect_to_db(**DB_CONFIG)

    # Загрузка ключевых слов для указанной категории
    category = 'Тест'
    keywords = get_keywords_by_category(conn, category)
    print(f"Загруженные ключевые слова для категории '{category}':", keywords)

    # Поиск ключевых слов в постах и комментариях
    posts = get_last_posts(vk, group_id, count=50)
    results = []
    processed_posts = set()

    for post in posts:
        post_id = post['id']
        is_pinned = post.get('is_pinned', False)

        # Проверка на уникальность поста
        if post_id in processed_posts:
            print(f"Пост ID: {post_id} уже был обработан, пропускаем.")
            continue

        # Добавление поста в множество уникальных после всех проверок
        processed_posts.add(post_id)

        # Засекаем время начала обработки поста
        start_time = time.time()

        # Проверка на репост
        if 'copy_history' in post:
            original_post = post['copy_history'][0]
            post_text = original_post['text'].lower()
            print(f"Обрабатывается репост оригинального поста ID: {original_post['id']}")
        else:
            post_text = post['text'].lower()

        post_url = f"https://vk.com/wall-{group_id}_{post_id}"
        print(f"Обрабатывается пост ID: {post_id}, закрепленный: {is_pinned}")

        # Проверка ключевых слов в тексте поста
        for keyword in keywords:
            if keyword.lower() in post_text:
                results.append((f"Пост ID: {post_id}", keyword, post_url))

        # Получение комментариев к посту и поиск ключевых слов, включая ответы на комментарии
        comments = get_comments(vk, -group_id, post_id, count=550)
        for comment in comments:
            comment_text = comment['text'].lower()
            comment_id = comment['id']
            comment_url = f"{post_url}?reply={comment_id}"
            print(f"Обрабатывается комментарий ID: {comment_id}")

            # Проверка ключевых слов в тексте комментария
            for keyword in keywords:
                if keyword.lower() in comment_text:
                    results.append((f"Комментарий ID: {comment_id}", keyword, comment_url))

            # Проверка ответов на комментарий
            thread_count = comment.get('thread', {}).get('count', 0)
            if thread_count > 0:
                thread_comments = get_comments(vk, -group_id, post_id, count=thread_count, thread_comment_id=comment_id)
                for thread_comment in thread_comments:
                    thread_text = thread_comment['text'].lower()
                    thread_id = thread_comment['id']
                    thread_url = f"{post_url}?reply={thread_id}"
                    print(f"Обрабатывается ответ на комментарий ID: {thread_id}")

                    for keyword in keywords:
                        if keyword.lower() in thread_text:
                            results.append((f"Ответ на комментарий ID: {thread_id}", keyword, thread_url))

        # Засекаем время окончания обработки поста
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Время обработки поста ID {post_id} и его комментариев: {elapsed_time:.2f} секунд")

    # Засекаем общее время выполнения программы
    total_end_time = time.time()
    total_elapsed_time = total_end_time - total_start_time
    print(f"Общее время выполнения программы: {total_elapsed_time:.2f} секунд")

    # Вывод результатов
    if results:
        print("Найденные совпадения:")
        for item_id, keyword, url in results:
            print(f"{item_id}, ключевое слово: {keyword}, ссылка: {url}")
    else:
        print("Совпадений не найдено.")

    # Закрытие подключения к базе данных
    conn.close()

if __name__ == "__main__":
    main()
