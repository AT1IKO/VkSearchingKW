from db_functions import add_keywords_to_db

# Пример ключевых слов и категория для теста
keywords = [
    "помощь1"
]
category = "Помощь1"

# Тестирование функции добавления ключевых слов в БД
add_keywords_to_db(keywords, category)

print("Тест завершён. Проверьте базу данных для подтверждения.")
