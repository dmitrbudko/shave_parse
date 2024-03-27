import requests
from bs4 import BeautifulSoup as BS
import re
import sqlite3

import config
def insert_db(names, articles, manufacturers, prices):
    # Устанавливаем соединение с базой данных
    with sqlite3.connect(config.db_path) as connection:
        cursor = connection.cursor()
    cursor = connection.cursor()

    # Создаем таблицу, если она еще не существует
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS source (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            article TEXT NOT NULL,
            manufacturer TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)

    # Добавляем новые записи в таблицу
    for name, article, manufacturer, price in zip(names, articles, manufacturers, prices):
        cursor.execute('INSERT INTO source (name, article, manufacturer, price) VALUES (?, ?, ?, ?)', (name, article, manufacturer, price))

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()


def parser():
    print("Процесс парсинга начат")
    # CSS селектор гиперссылки для элемента товара
    link_css_selector = "div.product-frame > div > a"
    # Список URL для обработки

    # Список для хранения гиперссылок для каждой ссылки
    hyperlinks = []
    # Списки для хранения данных
    names = []
    articles = []
    manufacturers = []
    prices = []

    # Проходим по каждой ссылке из списка links
    for link in config.links:
        response = requests.get(link)
        html = BS(response.content, 'html.parser')
        link_elements = html.select(link_css_selector)

        for link_element in link_elements:
            href = link_element.get('href')
            if href:
                hyperlinks.append(href)

    # Дополняем ссылки до полных
    base_url = "https://xn--80abdx3bn.xn--p1ai"
    full_urls = [base_url + link for link in hyperlinks]
    #Проходимся по всем полученным гиперссылкам и собираем нужную информацию
    for url in full_urls:
        print(f"Парсинг данных с гиперссылки: {url}")
        # Отправляем GET-запрос и получаем HTML-код страницы
        response = requests.get(url)
        html = BS(response.content, 'html.parser')

    # Находим нужные элементы на странице и извлекаем данные
        title = html.select_one('.single-product-card h2').text.strip()
        article = html.select_one('.single-product-card dd:nth-child(2)').text.strip()
        brand_element = html.find('dt', string='Бренд:')
        if brand_element:
            manufacturer = brand_element.find_next_sibling('dd').text.strip()
        else:
            manufacturer = "-"
        data3 = html.select_one('div.top-holder').text.strip()
        price = "".join(data3.strip().split())
        matches = re.findall(r'^\d+', price)
        number = int(matches[0])
    # Добавляем собранные данные в списки
        names.append(title)
        articles.append(article)
        manufacturers.append(manufacturer)
        prices.append(number)

    # Добавляем собранные данные в базу данных
    insert_db(names, articles, manufacturers, prices)


def print_all():
    connection = sqlite3.connect(config.db_path)
    cursor = connection.cursor()
    cursor.execute('SELECT name, price FROM source')
    answers = cursor.fetchall()
    connection.close()
    return answers


def search_func(query):
    answ = print_all()
    result = []
    for x in answ:
        if query.lower() in x[0].lower():
            result.append(x)
    return result


def the_output_is_less_than_price(query):
    query = float(query)
    connection = sqlite3.connect(config.db_path)
    cursor = connection.cursor()
    cursor.execute('''                                                              
    SELECT name, price
    FROM source
    GROUP BY price
    HAVING AVG(price) < ?
    ORDER BY price DESC
    ''', (query,))
    results = cursor.fetchall()
    connection.close()
    return results


def find_items_with_keywords(keywords):
    connection = sqlite3.connect(config.db_path)
    cursor = connection.cursor()
    # Создаем параметр для передачи ключевых слов в запрос SQL
    keyword_param = '%' + keywords + '%'
    cursor.execute('''
        SELECT name, price
        FROM source
        WHERE name LIKE ? 
    ''', (keyword_param,))
    results = cursor.fetchall()
    connection.close()
    return results




"""
print("Печать всех элементов:")
print(print_all())

# Поиск элементов по запросу
search_query = "Станок"
print(f"\nПоиск элементов по запросу '{search_query}':")
print(search_func(search_query))

# Поиск элементов с ценой меньше указанной
max_price = 1000  # Установи максимальную цену, например, 1000
print(f"\nПоиск элементов с ценой меньше {max_price}:")
print(the_output_is_less_than_price(max_price))

# Поиск элементов по ключевым словам
keywords = "Бритва"
print(f"\nПоиск элементов по ключевым словам '{keywords}':")
print(find_items_with_keywords(keywords))
"""
