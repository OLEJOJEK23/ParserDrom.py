from bs4 import BeautifulSoup
from dotenv import load_dotenv
from typing import List, Union
from requests import get, Response

load_dotenv()

URL = 'https://spb.drom.ru/all/'
cookies = {
    '_ga': 'GA1.1.715992914.1712953529',
    'ring': '935d4a9cW%2FWj9uKem1aqIxoMiwmSA0a6',
    'cookie_cityid': '2',
    'cookie_regionid': '78',
    'my_geo': '78',
    'dr_df': '1',
    'segSession': 'IjhhZDBlZjY1ZDI3OTgxMWFjNDRmMDlkMThjZTA3MzNhbm90QXV0aDkzNWQ0YTljV1wvV2o5dUtlbTFhcUl4b01pd21TQTBhNiJfODQzOWE0M2RjMDVlNDUzOWJiNWQzMWVlM2M1ZWZlMTY',
    'drom_search_web': '4',
    '_ga_1G91VLKB2K': 'GS1.1.1712953528.1.1.1712953578.10.0.0',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    # 'Cookie': '_ga=GA1.1.715992914.1712953529; ring=935d4a9cW%2FWj9uKem1aqIxoMiwmSA0a6; cookie_cityid=2; cookie_regionid=78; my_geo=78; dr_df=1; segSession=IjhhZDBlZjY1ZDI3OTgxMWFjNDRmMDlkMThjZTA3MzNhbm90QXV0aDkzNWQ0YTljV1wvV2o5dUtlbTFhcUl4b01pd21TQTBhNiJfODQzOWE0M2RjMDVlNDUzOWJiNWQzMWVlM2M1ZWZlMTY; drom_search_web=4; _ga_1G91VLKB2K=GS1.1.1712953528.1.1.1712953578.10.0.0',
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
pages = 10
marks = []
fuckingmarks = ['Alfa Romeo', 'Aston Martin', 'DW Hower', 'IM MOTORS', 'Iran Khodro', 'Land Rover', 'Lynk & Co','Great Wall']

def get_content(html: bytes) -> List[dict]:
    soup = BeautifulSoup(html, 'html.parser')
    blocks = soup.find_all('a', class_='css-4zflqt e1huvdhj1')
    items = []
    for item in blocks:
        if item.find('div', 'css-16kqa8y e3f4v4l2') is not None:
            name = item.find('div', 'css-16kqa8y e3f4v4l2').get_text()
        else:
            name = "чуй"
        for idi in fuckingmarks:
            if idi in name:
                name = name.replace(idi,"")
                if idi not in marks:
                    marks.append(idi)
                    break
        else:
            mark = name.split()[0]
            if mark not in marks:
                marks.append(mark)
            name = name.replace(mark,"")
        car = {
            'car': name,
            'price': item.find('span', 'css-46itwz e162wx9x0').get_text().replace(' ', '').replace('₽', ''),
            'desc': item.find('div', 'css-1fe6w6s e162wx9x0').get_text()
        }
        items.append(car)
        print(car)
    print(marks)
    return items


def get_html(url: str, headers: dict, params: Union[None, dict] = None) -> Response:
    """Getting an answer to the request."""
    try:
        return get(url, headers=headers, params=params, cookies=cookies)
    except Exception as error:
        raise ConnectionError(f'При выполнении запроса произошла ошибка: {error}')


def parse(url: str) -> List[dict]:
    """Parsing the request."""
    url = url or URL
    html = get_html(url, headers)
    with open("waeda.html","+w") as r:
        r.write(str(html.content))
    if html.status_code == 200:
        items = []
        pages_amount = pages
        for i in range(1, pages_amount + 1):
            print(f'Парсим {i} страницу из {pages_amount}...')
            print(url + f"page{i}/")
            html = get_html(url + f"page{i}/", headers)
            items.extend(get_content(html.content))
        print(f'Получены данные по {len(items)} авто.')
        return items
    else:
        print(f'Сайт вернул статус-код {html.status_code}')


def main():
    parse(URL)



if __name__ == '__main__':
    main()
