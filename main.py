import requests
import json
from collections import OrderedDict
from functools import partial

HOST = 'https://qiita.com'

json_loads = partial(json.loads, object_pairs_hook=OrderedDict)


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


tags = get_tags()
with open('./tags.json', mode='w', encoding='utf-8') as f:
    json.dump(tags, f, ensure_ascii=False, indent=4)
