team = 'YOUR_TEAMNAME'
access_token = 'YOUR_ACCESS_TOKEN'

start_date = '2018-01-01'
end_date = '2018-03-31'

import sys
import re
import json

import pandas as pd
import numpy as np

!pip install - q qiita_v2 retry
from qiita_v2.client import QiitaClient
from qiita_v2.exception import QiitaApiException
from retry import retry

c = QiitaClient(team=team, access_token=access_token)


@retry(delay=1, backoff=2, max_delay=8)
def list_items(yyyymm, page=1, per_page=100):
    print('fetching yyyymm:{} page:{}'.format(yyyymm, page), file=sys.stderr)
    r = c.list_items(
        params={
            'page': page,
            'per_page': per_page,
            'query': 'created:{}'.format(yyyymm),
        })
    return r


for dt in pd.date_range(start=start_date, end=end_date, freq='MS', tz='Asia/Tokyo'):
    yyyymm = dt.strftime('%Y-%m')
    filename = 'qiita-{}.json'.format(yyyymm)

    with open(filename, 'w', encoding='utf8') as f:
        posts = list_items(yyyymm, page=1)
        m = re.search(r"\?page=(\d+)", posts.link_last)
        if m:
            last_page = int(m.group(1)) + 1
        else:
            last_page = 2

        for page in range(1, last_page):
            posts = list_items(yyyymm, page=page)
            for post in posts.to_json():
                t = json.dumps(post, sort_keys=True, ensure_ascii=False) + "\n"
                f.write(t)