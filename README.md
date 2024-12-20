# rabbitmq-queue-work-example: Пример работы с очередью в RabbitMQ путем вставки ссылок на ресурсы в качестве значений очереди <br>
### В реализации представлено два консольных приложения: <br>
- url_parser.py - консольное приложение, принимающее на входе любой HTTP(S) URL, находит все внутренние ссылки (только для этого домена) в HTML-коде (a[href]), помещает их в очередь RabbitMQ по одной. <br>
- producer_consumer.py - консольное приложение: "вечный" асинхронный producer/consumer, читает ссылки, которые помещает в очередь скрипт url_parser.py, также находит внутренние ссылки и помещает в их очередь.
## Стек
Python 3.10 <br>
RabbitMQ <br>
BeautifulSoup <br>
asyncio <br>
logger <br>
## Использование:
1. Клонируйте репозиторий: <br>
```git clone https://github.com/evgeshkins/rabbitmq-queue-work-example.git . ``` <br>
2. Создайте виртуальное окружение: <br>
```python -m venv venv``` <br>
либо <br>
```py -m venv venv``` <br>
3. Активируйте виртуальное окружение: <br>
На Windows: <br>
```.venv\Scripts\activate``` <br>
На Linux: <br>
```source venv/bin/activate``` <br>
4. Установите библиотеки: <br>
```pip install -r requirements.txt``` <br>
5. Создайте файл .env в корне проекта и внесите туда значения следующих переменных: <br>
```python
RABBITMQ_HOST="адрес хоста"
RABBITMQ_QUEUE="название очереди"
TIMEOUT="время таймаута (указывать без кавычек)"
```
6. Запустите скрипт url_parser.py и передайте в него URL в качестве аргумента: <br>
```python
python url_parser.py "URL"
```
Пример: <br>
```python
python url_parser.py "https://www.rabbitmq.com/docs/install-windows"
```
7. Запустите скрипт из producer_consumer.py из другого терминала/консоли: <br>
```python
python producer_consumer.py
```
*Вы можете прерывать выполнение этого скрипта с помощью комбинации клавиш CTRL + C.


