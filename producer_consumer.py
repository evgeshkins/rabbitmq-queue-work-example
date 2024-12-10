import aiohttp
from bs4 import BeautifulSoup
import asyncio
import os
import pika
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("pika").setLevel(logging.WARNING)

load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "url_queue")
TIMEOUT = int(os.getenv("TIMEOUT", "30"))  # Таймаут ожидания в секундах

def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(base_url, href)
        if urlparse(full_url).netloc == urlparse(base_url).netloc:
            links.append((a_tag.get_text(strip=True), full_url))
    return links

async def fetch_html(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def process_page(url):
    """
    Асинхронная обработка URL.
    """
    logger.info(f"Обрабатывается: {url}")
    try:
        html = await fetch_html(url)
        links = extract_links(html, url)
        for name, link in links:
            logger.info(f"Найдена ссылка: {name or 'No name'} -> {link}")
    except Exception as e:
        logger.info(f"Ошибка обработки {url}: {e}")

async def consume():
    """
    Основной цикл потребления сообщений из очереди с учётом таймаута и завершения по CTRL+C.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    
    logger.info(f"Подключено к RabbitMQ. Ожидаю сообщения: timeout {TIMEOUT} секунд...")
    loop = asyncio.get_event_loop()
    timeout_counter = 0  # Счётчик таймаута

    try:
        while True:
            method_frame, properties, body = channel.basic_get(queue=RABBITMQ_QUEUE, auto_ack=True)

            if body:
                url = body.decode()
                logger.info(f"Принято: {url}")
                timeout_counter = 0  # Сброс таймаута при получении сообщения
                await process_page(url)
            else:
                timeout_counter += 1
                logger.info(f"Очередь пуста. Ожидаю {timeout_counter}/{TIMEOUT} секунд...")
                await asyncio.sleep(1)

            if timeout_counter >= TIMEOUT:
                logger.info("Timeout превышен. Останавливаю consumer...")
                break
    except KeyboardInterrupt:
        logger.info("\nНажата комбинация CTRL+C. Останавливаю consumer...")
    finally:
        channel.close()
        connection.close()
        logger.info("Подключение закрыто. Выход...")

if __name__ == '__main__':
    try:
        asyncio.run(consume())
    except KeyboardInterrupt:
        logger.info("\nНажата комбинация CTRL+C. Останавливаю программу...")