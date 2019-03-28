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


def daterange(start_date, end_date):
    for n in range((end_date - start_date).days + 1):
        yield start_date + timedelta(n)


def month_span(start_date, end_date):
    """start_date、end_dateの期間に含まれる月毎のdatetimeオブジェクトを返すジェネレータ
    """
    yield start_date
    while(start_date.year != end_date.year or
          start_date.month != end_date.month):
        start_date = start_date + relativedelta(months=1)
        yield start_date


def get_tags():
    uri = '/api/v2/tags'
    params = {
        'page': 1,
        'per_page': 100,
        'sort': 'count'
    }
    response = requests.get(url=HOST + uri, params=params)
    if response.status_code == 200:
        return json_loads(response.text)
    else:
        return response


def get_items_per_month(yyyymm, page=1, per_page=100):
    print('fetching yyyymm:{} page:{}'.format(yyyymm, page))
    uri = '/api/v2/items'

    # 指定年月の最大ページ数を取得
    params = {
        'page': page,
        'per_page': per_page,
        'query': 'created:{}'.format(yyyymm)
    }
    response = requests.get(url=HOST+uri, params=params)

    # res_headers = response.headers
    total_count = int(response.headers['Total-Count'])
    quotient, remainder = divmod(total_count, per_page)
    max_page_count = quotient if remainder == 0 else quotient + 1

    monthly_items = []
    for page in range(1, max_page_count + 1):
        if page > 2:
            break
        params = {
            'page': page,
            'per_page': per_page,
            'query': 'created:{}'.format(yyyymm)
        }
        sleep(5)
        response = requests.get(url=HOST + uri, params=params)
        data = json_loads(response.text)
        monthly_items.extend(data)
    return monthly_items


# main
start = datetime.strptime('2019-01', '%Y-%m')
end = datetime.strptime('2019-03', '%Y-%m')

for date in month_span(start, end):
    items = get_items_per_month(date.strftime('%Y-%m'), per_page=2)
    with open('./items_{}.json'.format(date.strftime('%Y-%m')), mode='w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=4)
