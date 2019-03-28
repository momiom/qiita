import requests
import json
from collections import OrderedDict
from functools import partial
from datetime import datetime, timedelta
from time import sleep

from dateutil.relativedelta import relativedelta

HOST = 'https://qiita.com'
TOKEN = '3973ea4379d9c87d5d8752c239ced72d1bc00791'

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
    """start_date、end_dateの期間に含まれる月毎のdatetimeオブジェクトを返すジェネレータ
    """
    yield start_date
    while(start_date.year != end_date.year or
          start_date.month != end_date.month):
        start_date = start_date + relativedelta(months=1)
        yield start_date


def get_items_per_month(yyyymm, page=1, per_page=100):
    print('Fetching items per month...')
    print('Target: {}'.format(yyyymm))
    uri = '/api/v2/items'

    # 期間の設定
    # ひと月分取得するには対象月の前日（先月末）から対象月の月末までを指定する
    target_month = datetime.strptime(yyyymm, '%Y-%m')
    st = (target_month - relativedelta(days=1)).strftime('%Y-%m-%d')
    ed = (target_month + relativedelta(months=1, days=-1)).strftime('%Y-%m-%d')

    # 指定年月の最大ページ数を取得
    payload = {
        'page': page,
        'per_page': per_page,
        'query': 'created:>{}+created:<{}'.format(st, ed)
    }
    payload_str = '&'.join('{}={}'.format(k, v) for k, v in payload.items())

    response = req_get(url=HOST+uri, payload=payload_str)
    print('First URL: {}'.format(response.url))

    total_count = int(response.headers['Total-Count'])
    print('total_count: {}'.format(total_count))

    quotient, remainder = divmod(total_count, per_page)
    print('quotient: {}, remainder: {}'.format(quotient, remainder))

    max_page_count = quotient if remainder == 0 else quotient + 1
    print('Max page count: {}'.format(max_page_count))

    monthly_items = []
    for page in range(1, max_page_count + 1):
        if page > 1:
            break
        payload = {
            'page': page,
            'per_page': per_page,
            'query': 'created:>{}+created:<{}'.format(st, ed)
        }
        payload_str = '&'.join('{}={}'.format(k, v) for k, v in payload.items())
        response = req_get(url=HOST + uri, payload=payload_str)
        data = json_loads(response.text)
        monthly_items.extend(data)

    print('Final URL: {}'.format(response.url))
    print('Done.\n')
    return monthly_items


# main
start = datetime.strptime('2019-01', '%Y-%m')
end = datetime.strptime('2019-03', '%Y-%m')

for date in month_span(start, end):
    items = get_items_per_month(date.strftime('%Y-%m'), per_page=1)
    with open('./items_{}.json'.format(date.strftime('%Y-%m')), mode='w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=4)
