import os
import requests
import json
from collections import OrderedDict
from functools import partial
from datetime import datetime, timedelta
from time import sleep
from tqdm import tqdm
import settings

from dateutil.relativedelta import relativedelta

HOST = 'https://qiita.com'
TOKEN = settings.api_token

json_loads = partial(json.loads, object_pairs_hook=OrderedDict)

HEADER = {
    'Authorization': 'Bearer {}'.format(TOKEN)
}

last_api_call = datetime.now()


def req_get(url, payload):
    global last_api_call
    elapsed_sec = (last_api_call - datetime.now()).total_seconds()
    if elapsed_sec <= 3.6:
        sleep(3.6 - elapsed_sec)
    res = requests.get(url=url, params=payload, headers=HEADER)
    last_api_call = datetime.now()
    return res


def month_span(start_date, end_date):
    """
    start_date ~ end_dateのYYYYMMのdatetimeオブジェクトを返すジェネレータ

    :param start_date: datetime
    :param end_date: datetime

    :return datetime
    """
    yield start_date
    while(start_date.year != end_date.year or
          start_date.month != end_date.month):
        start_date = start_date + relativedelta(months=1)
        yield start_date


def notify(message, mention=False):
    url = settings.slack_webhook_url
    headers = {'content-type': 'application/json'}
    payload = {
        'text': f'<@UCLAPNDCJ> {message}' if mention else f'{message}'
    }
    requests.post(url, data=json.dumps(payload), headers=headers)


def get_items_per_month(yyyymm, page=1, max_page=float('inf'), per_page=100):
    print('Fetching items per month...')
    print(f'Target: {yyyymm}')
    uri = '/api/v2/items'

    per_page = per_page if per_page <= 100 else 100

    # 期間の設定
    # ひと月分取得するには対象月の前日（先月末）から対象月の月末までを指定する
    target_month = datetime.strptime(yyyymm, '%Y-%m')
    st = (target_month - relativedelta(days=1)).strftime('%Y-%m-%d')
    ed = (target_month + relativedelta(months=1, days=-1)).strftime('%Y-%m-%d')

    # 指定年月の最大ページ数を取得
    payload = {
        'page': page,
        'per_page': per_page,
        'query': f'created:>{st}+created:<{ed}'
    }
    payload_str = '&'.join(f'{k}={v}' for k, v in payload.items())

    response = req_get(url=HOST+uri, payload=payload_str)
    print(f'First URL: {response.url}')

    total_count = int(response.headers['Total-Count'])
    print(f'total_count: {total_count}')

    quotient, remainder = divmod(total_count, per_page)
    print(f'quotient: {quotient}, remainder: {remainder}')

    max_page_count = quotient if remainder == 0 else quotient + 1
    print(f'Max page count: {max_page_count}')

    monthly_items = []
    for page in tqdm(range(1, max_page_count + 1)):
        if page > max_page:
            break

        payload = {
            'page': page,
            'per_page': per_page,
            'query': f'created:>{st}+created:<{ed}'
        }
        payload_str = '&'.join(f'{k}={v}' for k, v in payload.items())
        response = req_get(url=HOST + uri, payload=payload_str)
        data = json_loads(response.text)
        monthly_items.extend(data)

    print(f'Last URL: {response.url}')
    print('Done.\n')
    return monthly_items


def main():
    # main
    start = datetime.strptime('2020-01', '%Y-%m')
    end = datetime.strptime('2020-02', '%Y-%m')
    # 取得記事数 = max_page * per_page * len(month_span)
    # max_page = float('inf')  # 取得するページ数
    max_page = 1  # 取得するページ数
    per_page = float('inf')  # 1ページ数あたりの記事数
    notify(f'START\nFrom: {start}\nTo:   {end}')
    try:
        for date in month_span(start, end):
            curr_date = date.strftime('%Y-%m')
            items = get_items_per_month(curr_date, max_page=max_page, per_page=per_page)
            os.makedirs('data', exist_ok=True)
            with open(f'./data/items_{curr_date}.json', mode='w', encoding='utf-8') as f:
                json.dump(items, f, ensure_ascii=False, indent=4)
            notify(f'{curr_date}  Count: {len(items)}\n')
        notify('Done!', mention=True)
    except Exception as e:
        notify(str(e), mention=True)
        raise


if __name__ == '__main__':
    main()
