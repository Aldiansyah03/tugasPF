import asyncio
import time
from random import randint
import multiprocessing


import httpx
import requests
from flask import Flask

app = Flask(__name__)

img_list_count = 10


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


def get_xkcd_image():
    random = randint(0, 300)
    response = requests.get(f'https://xkcd.com/{random}/info.0.json')
    return response.json()['img']


def get_multiple_images(number):
    return [get_xkcd_image() for _ in range(number)]


@app.get('/comic')
def hello():
    start = time.perf_counter()
    urls = get_multiple_images(img_list_count)
    end = time.perf_counter()

    markup = f"Time taken: {end-start}<br><br>"
    for url in urls:
        markup += f'<img src="{url}"></img><br><br>'

    return markup


async def get_xkcd_image_async(session):
    random = randint(0, 300)

    result = await session.get(f'https://xkcd.com/{random}/info.0.json')
    return result.json()['img']


async def get_multiple_images_async(number):
    async with httpx.AsyncClient() as session:
        tasks = [get_xkcd_image_async(session) for _ in range(number)]
        result = await asyncio.gather(*tasks, return_exceptions=True)
    return result


@app.get('/comic_async')
async def hello_async():
    start = time.perf_counter()
    urls = await get_multiple_images_async(img_list_count)
    end = time.perf_counter()
    markup = f"Time taken: {end-start}<br><br>"
    for url in urls:
        markup += f'<img src="{url}"></img><br><br>'

    return markup


def get_xkcd_image_multiprocess(output, idx):
    random = randint(0, 300)
    response = requests.get(f'https://xkcd.com/{random}/info.0.json')
    output.put((idx, response.json()['img']))


def get_multiple_images_multiprocess(number):
    output = multiprocessing.Queue()
    processes = []

    for i in range(number):
        process = multiprocessing.Process(
            target=get_xkcd_image_multiprocess, args=(output, i))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    results = [None] * number
    while not output.empty():
        idx, img_url = output.get()
        results[idx] = img_url

    return results


@app.get('/comic_multiprocess')
def hello_multiprocess():
    start = time.perf_counter()
    urls = get_multiple_images_multiprocess(img_list_count)
    end = time.perf_counter()

    markup = f"Time taken: {end-start}<br><br>"
    for url in urls:
        markup += f'<img src="{url}"></img><br><br>'

    return markup


if __name__ == '__main__':
    app.run(debug=True)
