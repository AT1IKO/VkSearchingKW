import requests

def get_group_id_by_screen_name(vk_token, group_screen_name):
    url = 'https://api.vk.com/method/groups.getById'
    params = {
        'group_id': group_screen_name,
        'access_token': vk_token,
        'v': '5.131'
    }

    response = requests.get(url, params=params)
    data = response.json()

    if 'response' in data:
        return data['response'][0]['id']
    else:
        raise Exception(f"Ошибка получения ID группы: {data}")



