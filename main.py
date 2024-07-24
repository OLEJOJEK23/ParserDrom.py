import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from typing import List, Union
from requests import get, Response
import pyodbc

load_dotenv()

URL = 'https://spb.drom.ru/all/'
cookies = {
    #cookies
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'If-Modified-Since': 'Sat, 13 Apr 2024 06:26:09 GMT',
    'Referer': 'https://auto.drom.ru/all/page2/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}
pages = 2
marks = {}
fuckingmarks = ['Alfa Romeo', 'Aston Martin', 'DW Hower', 'IM MOTORS', 'Iran Khodro', 'Land Rover', 'Lynk & Co','Great Wall']


def get_state(name):
    if 'км' in name:
        return 'БУ'
    else:
        return 'Новая'
def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k
def get_content(html: bytes) -> List[dict]:
    soup = BeautifulSoup(html, 'html.parser')
    blocks = soup.find_all('a', class_='css-4zflqt e1huvdhj1')
    items = []
    mark = ''
    if len(marks) < 1:
        id = 1
    else:
        id = max(marks.keys())
    for item in blocks:
        if item.find('div', 'css-16kqa8y e3f4v4l2') is not None:
            name = item.find('div', 'css-16kqa8y e3f4v4l2').get_text()
        else:
            name = "чуй"
        for idi in fuckingmarks:
            if idi in name:
                name = name.replace(idi,"")
                if idi not in marks.values():
                    marks.update({id: idi})
                    id+=1
                    break
        else:
            mark = name.split()[0]
            if mark not in marks.values():
                marks.update({id: mark})
                id+=1
            name = name.replace(mark,"")
        car = {
            'car': name,
            'price': item.find('span', 'css-46itwz e162wx9x0').get_text().replace(' ', '').replace('₽', ''),
            'desc': item.find('div', 'css-1fe6w6s e162wx9x0').get_text(),
            'CollectionID': get_key(marks, mark),
            'state': get_state(item.find('div', 'css-1fe6w6s e162wx9x0').get_text())
        }
        items.append(car)
    id = 0
    for item in soup.find_all('img','css-9w7beg evrha4s0'):
        url = item.get('src')
        img = requests.get(url,stream=True)
        file = open(f"pictures/{id}.jpg",'bw')
        for chunk in img.iter_content(4096):
            file.write(chunk)
        id += 1
    return items


def get_html(url: str, headers: dict, params: Union[None, dict] = None) -> Response:
    try:
        return get(url, headers=headers, params=params, cookies=cookies)
    except Exception as error:
        raise ConnectionError(f'При выполнении запроса произошла ошибка: {error}')


def parse(url: str) -> List[dict]:
    url = url or URL
    html = get_html(url, headers)
    if html.status_code == 200:
        items = []
        pages_amount = pages
        for i in range(1, pages_amount + 1):
            print(f'Парсим {i} страницу из {pages_amount}...')
            html = get_html(url + f"page{i}/", headers)
            items.extend(get_content(html.content))
        print(f'Получены данные по {len(items)} авто.')
        return items
    else:
        print(f'Сайт вернул статус-код {html.status_code}')


def insert_into_bd(data: list):
    try:
        print("Подключаюсь к БД")
        connection = pyodbc.connect(r'Driver={SQL Server};Server=DESKTOP-3K9H0H0;Database=Autosalon;Trusted_Connection=yes;')
        try:
            with connection.cursor() as cur:
                for item in marks.values():
                    query = f"INSERT INTO Creatore(CreatoreName) VALUES ('{item}');"
                    cur.execute(query)
                    connection.commit()
                for i in range(len(data)):
                    query = f"INSERT INTO Car(CreatoreID, Name, Price, Status, Description,Image_var) VALUES ('{data[i]['CollectionID']}','{data[i]['car']}','{data[i]['price']}','{data[i]['state']}','{data[i]['desc']},f'pictures/{i}.jpg');"
                    cur.execute(query)
                    connection.commit()
        finally:
            connection.close()
    except Exception as ex:
        print(ex)


def main():
    insert_into_bd(parse(URL))


if __name__ == '__main__':
    main()
