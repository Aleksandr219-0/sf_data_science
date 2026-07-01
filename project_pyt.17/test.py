
import requests # Импортируем модуль requests
token = 'c7a144e7c7a144e7c7a144e716c4e34df5cc7a1c7a144e7ade21b9b8d49c2ae1d5cbc05'
url = 'https://api.vk.com/method/users.get' # Указываем адрес страницы к которой делаем запрос
params = {'user_id': 1, 'v': 5.95, 'fields': 'sex,bdate', 'access_token': token, 'lang': 'ru'} # Перечисляем параметры нашего запроса в словаре params
response = requests.get(url, params=params) # Отправляем запрос
print(response.text) 

pip install schedule
