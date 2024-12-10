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

async def fetch_html(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text(), str(response.url)
        
def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(base_url, href)
        if urlparse(full_url).netloc == urlparse(base_url).netloc:
            links.append((a_tag.get_text(strip=True), full_url))
    return links

def send_to_queue(links):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    for name, link in links:
        channel.basic_publish(exchange='', routing_key=RABBITMQ_QUEUE, body=link)
        logger.info(f"В очередь: {name or 'No name'} -> {link}")
    connection.close()

async def main(url):
    html, base_url = await fetch_html(url)
    links = extract_links(html, base_url)
    send_to_queue(links)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        logger.info("Неверное количество аргументов! Используйте: python url_parser.py <URL>")
        sys.exit(1)
    url = sys.argv[1]
    asyncio.run(main(url))