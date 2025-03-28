# telegram_bot/bot/utils/api_client.py

import aiohttp
import os
import logging

logger = logging.getLogger(__name__)

# Загрузка переменных окружения
API_URL = os.getenv('API_URL')
ADMIN_API_TOKEN = os.getenv('ADMIN_API_TOKEN')  # Добавляем загрузку ADMIN_API_TOKEN

class APIClient:
    def __init__(self, token: str):
        self.token = token
        self.session = aiohttp.ClientSession()

    async def get_products(self):
        """
        Получает список доступных продуктов через API.
        Предполагается наличие эндпоинта /products/api/list/
        """
        url = f"{API_URL}/products/api/list/"
        headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json'
        }
        logger.debug(f"Отправка GET-запроса на {url} с заголовками: {headers}")
        async with self.session.get(url, headers=headers) as response:
            logger.debug(f"Ответ от API: статус {response.status}")
            if response.status == 200:
                data = await response.json()
                logger.info(f"Получены продукты: {data}")
                return data.get('results', [])
            else:
                error = await response.text()
                logger.error(f"Получение продуктов не удалось: {error}")
                raise Exception(f"Не удалось получить продукты: {error}")

    async def create_order(self, order_items, address, city, postal_code, phone_number):
        """
        Создаёт новый заказ через API с данными доставки.
        """
        url = f"{API_URL}/orders/api/create/"
        headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json'
        }
        payload = {
            'order_items': order_items,
            'address': address,
            'city': city,
            'postal_code': postal_code,
            'phone_number': phone_number
        }
        logger.debug(f"Отправка POST-запроса на {url} с заголовками: {headers} и данными: {payload}")
        async with self.session.post(url, json=payload, headers=headers) as response:
            logger.debug(f"Ответ от API: статус {response.status}")
            if response.status == 201:
                data = await response.json()
                logger.info(f"Создан заказ: {data}")
                return data
            else:
                error = await response.text()
                logger.error(f"Создание заказа не удалось: {error}")
                raise Exception(f"Не удалось создать заказ: {error}")

    async def get_order_status(self, order_id):
        url = f"{API_URL}/orders/api/status/{order_id}/"
        headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json'
        }
        logger.debug(f"Отправка GET-запроса на {url} с заголовками: {headers}")
        async with self.session.get(url, headers=headers) as response:
            logger.debug(f"Ответ от API: статус {response.status}")
            if response.status == 200:
                data = await response.json()
                logger.info(f"Получен статус заказа №{order_id}: {data}")
                return data
            else:
                error = await response.text()
                logger.error(f"Получение статуса заказа не удалось: {error}")
                raise Exception(f"Не удалось получить статус заказа: {error}")

    async def link_telegram_id(self, username: str, telegram_id: int):
        """
        Связывает Telegram ID с пользователем Django по username.
        """
        url = f"{API_URL}/users/api/link_telegram_id/"
        headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json'
        }
        payload = {
            'username': username,
            'telegram_id': telegram_id
        }
        logger.debug(f"Отправка POST-запроса на {url} с данными: {payload}")
        async with self.session.post(url, json=payload, headers=headers) as response:
            logger.debug(f"Ответ от API: статус {response.status}")
            if response.status == 200:
                data = await response.json()
                logger.info(f"Связано Telegram ID {telegram_id} с username '{username}'.")
                return data
            else:
                error = await response.text()
                logger.error(f"Связывание Telegram ID не удалось: {error}")
                raise Exception(f"Не удалось связать Telegram ID: {error}")

    async def get_user_orders(self):
        """
        Получает список заказов пользователя.
        Предполагается наличие эндпоинта /orders/api/user_orders/
        """
        url = f"{API_URL}/orders/api/user_orders/"
        headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json'
        }
        logger.debug(f"Отправка GET-запроса на {url} с заголовками: {headers}")
        async with self.session.get(url, headers=headers) as response:
            logger.debug(f"Ответ от API: статус {response.status}")
            if response.status == 200:
                data = await response.json()
                logger.info(f"Получены заказы пользователя: {data}")
                return data
            else:
                error = await response.text()
                logger.error(f"Получение заказов не удалось: {error}")
                raise Exception(f"Не удалось получить заказы: {error}")

    async def close(self):
        await self.session.close()

async def get_user_api_token(telegram_id: int) -> str:
    """
    Функция для получения API-токена пользователя по его Telegram ID.
    Предполагается наличие эндпоинта /users/api/get_token_by_telegram_id/?telegram_id=<id>
    """
    if not ADMIN_API_TOKEN:
        logger.error("ADMIN_API_TOKEN не установлен в переменных окружения.")
        return None

    url = f"{API_URL}/users/api/get_token_by_telegram_id/?telegram_id={telegram_id}"
    headers = {
        'Authorization': f'Token {ADMIN_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    logger.debug(f"Отправка GET-запроса на {url} с заголовками: {headers}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            logger.debug(f"Ответ от API: статус {response.status}")
            if response.status == 200:
                data = await response.json()
                token = data.get('token')
                if token:
                    logger.info(f"Получен токен для пользователя {telegram_id}: {token}")
                else:
                    logger.warning(f"Токен не найден для пользователя {telegram_id}.")
                return token
            else:
                error = await response.text()
                logger.error(f"Ошибка при получении токена для пользователя {telegram_id}: {error}")
                return None

async def get_product_id_by_name(product_name: str) -> int:
    """
    Функция для получения ID продукта по его названию через API Django.
    Предполагается наличие эндпоинта /products/api/search/?search=<name>
    """
    search_url = f"{API_URL}/products/api/search/?search={product_name}"
    logger = logging.getLogger(__name__)
    headers = {
        'Authorization': f'Token {ADMIN_API_TOKEN}',  # Добавляем заголовок, если требуется
        'Content-Type': 'application/json'
    }
    async with aiohttp.ClientSession() as session:
        logger.debug(f"Отправка GET-запроса на {search_url} с заголовками: {headers}")
        async with session.get(search_url, headers=headers) as response:
            logger.debug(f"Ответ от API: статус {response.status}")
            if response.status == 200:
                data = await response.json()
                if data.get('results'):
                    product_id = data['results'][0]['id']
                    logger.info(f"Найден продукт '{product_name}' с ID {product_id}.")
                    return product_id
            logger.error(f"Продукт '{product_name}' не найден. Ответ API: {response.status}")
            return None
