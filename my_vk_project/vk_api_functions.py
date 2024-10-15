import vk_api

def connect_to_vk(token):
    vk_session = vk_api.VkApi(token=token)
    return vk_session.get_api()

def get_last_posts(vk, group_id, count=10):
    posts = vk.wall.get(owner_id=-int(group_id), count=count)['items']
    return posts

def get_group_id(vk, group_name):
    group_info = vk.groups.getById(group_id=group_name)
    return group_info[0]['id']

def get_comments(vk, owner_id, post_id, count=100, thread_comment_id=None):
    """
    Получение комментариев к посту, с возможностью загрузки ответов на комментарии.
    :param vk: Объект подключения к VK API
    :param owner_id: ID владельца поста (группы)
    :param post_id: ID поста
    :param count: Количество загружаемых комментариев
    :param thread_comment_id: Если указан, загружает ответы на данный комментарий
    :return: Список комментариев
    """
    comments = []
    try:
        if thread_comment_id is None:
            # Получение обычных комментариев
            response = vk.wall.getComments(
                owner_id=owner_id,
                post_id=post_id,
                count=count,
                thread_items_count=10,  # Загружаем до 10 ответов на каждый комментарий
                extended=1
            )
        else:
            # Получение ответов на комментарий
            response = vk.wall.getComments(
                owner_id=owner_id,
                post_id=post_id,
                start_comment_id=thread_comment_id,
                count=count,
                extended=1
            )

        comments = response.get('items', [])
    except Exception as e:
        print(f"Ошибка при получении комментариев: {e}")

    return comments


