import requests
from requests import get, post, put
import sys
import os
import pygame

def size(response_my):
    resp = response_my['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['boundedBy']['Envelope']
    lx, ly = map(float, resp['lowerCorner'].split())
    rx, ry = map(float, resp['upperCorner'].split())
    w = abs(rx - lx)
    h = abs(ry - ly)
    return (w, h)

def scope(response_my):
    w, h = size(response_my)
    return w / 3 , h / 3

def position(response_my):
    return response_my['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']


def search(place):
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?geocode={}&format=json".format(place)
    response = get(geocoder_request)
    json_response = response.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
    x, y = json_response.split()
    return (str(x) + ',' + str(y), (float(x), float(y)))



me = 'Новосондецкий Бульвар 5, п. 4'




search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
address_ll = search(me)[0]
search_params = {
    "apikey": api_key,
    "text": "аптека",
    "lang": "ru_RU",
    "ll": address_ll,
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params).json()
data = response['features'][0]['properties']
name = data['name']
address = data['description']
worktime = 'Время работы: ' + data['CompanyMetaData']['Hours']['text']
x, y = data['boundedBy'][0]

response = None
try:
    map_request = "http://static-maps.yandex.ru/1.x/?l=map&pl={},{},{}&pt={},{},pm2bm~{},pm2am".format(x, y , address_ll,x, y , address_ll)
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)
except:
    print("Запрос не удалось выполнить. Проверьте наличие сети Интернет.")
    sys.exit(1)

# Запишем полученное изображение в файл.
map_file = "map.png"
try:
    with open(map_file, "wb") as file:
        file.write(response.content)
except IOError as ex:
    print("Ошибка записи временного файла:", ex)
    sys.exit(2)

# Инициализируем pygame
pygame.init()
screen = pygame.display.set_mode((600, 450))
# Рисуем картинку, загружаемую из только что созданного файла.
screen.blit(pygame.image.load(map_file), (0, 0))

f1 = pygame.font.Font(None, 25)
text1 = f1.render(name, 1, (0, 0, 0))
text2 = f1.render(address, 1, (0, 0, 0))
text3 = f1.render(worktime, 1, (0, 0, 0))
screen.blit(text1, (10, 15))
screen.blit(text2, (10, 40))
screen.blit(text3, (10, 65))
# Переключаем экран и ждем закрытия окна.
pygame.display.flip()
while pygame.event.wait().type != pygame.QUIT:
    pass
pygame.quit()

# Удаляем за собой файл с изображением.
os.remove(map_file)
