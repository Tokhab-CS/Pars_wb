import csv
import logging
import collections
import time

import bs4
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wb')

ParseResult = collections.namedtuple(
    'ParseResult',
    (
        'brand_name',
        'goods_name',
        'price',
        'reviews',
        'url'
    ),
)

HEADRES = (
    'Бренд',
    'Товар',
    'Цена',
    'Отзывы',
    'Ссылка'
)


class Client:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.0.1996 Yowser/2.5 Safari/537.36'
        }
        self.result = []

    def load_page(self, page: int = None):
        url = 'https://www.wildberries.ru/catalog/muzhchinam/odezhda/vodolazki'
        res = self.session.get(url=url)
        res.raise_for_status()

        return res.text

    def parse_page(self, text: str):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div.product-card.j-card-item')
        for block in container:
            self.parse_block(block=block)


    def parse_block(self, block):
        url_block = block.select_one('a.product-card__main')
        if not url_block:
            logger.error('no url block')
            return

        url = url_block.get('href')
        if not url:
            logger.error('no href')
            return
        url = 'https://www.wildberries.ru' + url
        # logger.info('%s', url)
        # self.get_card(url)


        reviews = url_block.select_one('span.product-card__count')
        if not reviews:
            logger.error('product-card__count')
            return
        reviews = reviews.text.replace(' ', '').strip()

        name_block = block.select_one('div.product-card__brand-name')
        if not name_block:
            logger.error(f'No name_block on {url}')
            return

        brand_name = name_block.select_one('strong.brand-name')
        if not name_block:
            logger.error(f'No brand_name on {url}')
            return

        brand_name = brand_name.text.replace('/', '').strip()

        goods_name = name_block.select_one('span.goods-name')
        if not goods_name:
            logger.error(f'No goods_name on {url}')
            return

        goods_name = goods_name.text.strip()

        price_block = block.select_one('div.j-cataloger-price')
        if not price_block:
            logger.error(f'No price_block on {url}')
            return

        price = price_block.select_one('span.price')
        if not price_block:
            logger.error(f'No price on {url}')
            return

        low_price = price.select_one('ins.lower-price')
        if not low_price:
            low_price = price.select_one('span.lower-price')
            if not low_price:
                logger.error(f'No any price on {url}')
                return

        low_price = low_price.text.replace(' ', '').replace('₽', '').strip()

        self.result.append(ParseResult(
            brand_name=brand_name,
            goods_name=goods_name,
            price=low_price,
            reviews=reviews,
            url=url
        ))

        # logger.debug('%s, %s, %s, %s, %s', url, brand_name, goods_name, low_price, reviews)
        # logger.debug('-' * 100)

    def save_result(self):
        path = r'D:\YandexDisk\Документы\Education\PyCharm\Parsing_WB\test.csv'
        with open(path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(HEADRES)
            for item in self.result:
                writer.writerows(self.result)

    def run(self):
        text = self.load_page()
        self.parse_page(text=text)
        logger.info(f'We have taken {len(self.result)} cards')

        self.save_result()

# class Cards:
#
#     def __init__(self):
#         self.session = requests.Session()
#         self.session.headers = {
#             'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.0.1996 Yowser/2.5 Safari/537.36'
#         }
#         self.result = []
#
#
#     def parse_card(self, card_block):
#         all_reviews = bs4.BeautifulSoup(card_block, 'lxml')
#         container = all_reviews.select('div.feedback__content')
#         for block_review in container:
#             print(block_review)
#             logger.info('%s', block_review)
#
#
#     def get_card(self, url):
#         card_block = self.session.get(url)
#         card_block.raise_for_status()
#         self.parse_card(card_block=card_block)
#


if __name__ == '__main__':
    parser = Client()
    parser.run()
    # main()
