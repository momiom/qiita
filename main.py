import requests
import json
from collections import OrderedDict
from functools import partial
from datetime import datetime, timedelta

HOST = 'https://qiita.com'

json_loads = partial(json.loads, object_pairs_hook=OrderedDict)


def daterange(start_date, end_date):
    for n in range((end_date - start_date).days + 1):
        yield start_date + timedelta(n)


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


def get_items(yyyymm, page=1, per_page=100):
    print('fetching yyyymm:{} page:{}'.format(yyyymm, page), file=sys.stderr)
    r = c.list_items(
        params={
            'page': page,
            'per_page': per_page,
            'query': 'created:{}'.format(yyyymm),
        })
    return r


start = datetime.strptime('2018-01', '%Y/%m')
end = datetime.strptime('2019-03', '%Y-%m')
for date in daterange(start, end):


tags = get_tags()
with open('./tags.json', mode='w', encoding='utf-8') as f:
    json.dump(tags, f, ensure_ascii=False, indent=4)
