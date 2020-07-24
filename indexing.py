import json
import multiprocessing
import time
from glob import glob
from elasticsearch import Elasticsearch, helpers


def create_index(index, mapping, setting):
    # settingsを指定してインデックスを作成
    es.indices.create(index=index, body=setting)

    # 作成したインデックスのマッピングを指定
    es.indices.put_mapping(index=index, body=mapping)


def load_data():
    monthly_data_list = []
    for d in glob('./data/**/*.json', recursive=True):
        with open(d) as f:
            monthly_data_list.append(json.load(f))

    for i, monthly_data in enumerate(monthly_data_list, start=1):
        print(f'monthly_data_list: {i}/{len(monthly_data_list)}')
        for j, d in enumerate(monthly_data, start=1):
            print(f'\rmonthly_data: {j}/{len(monthly_data)}', end='')
            yield {
                    '_index': 'qiita',
                    '_source': d
                }
        print()


def load_data2():
    monthly_data_list = []
    for d in glob('./data/**/*.json', recursive=True):
        with open(d, encoding='utf-8') as f:
            monthly_data_list.append(json.load(f))

    insert_data_list = []
    for monthly_data in monthly_data_list:
        for d in monthly_data:
            insert_data_list.append(
                {
                    '_index': 'qiita',
                    '_type': '_doc',
                    '_source': d
                }
            )
            if len(insert_data_list) >= 100:
                yield insert_data_list
                insert_data_list = []
                time.sleep(30)

    if len(insert_data_list) > 0:
        yield insert_data_list


def main():
    global es
    host = 'localhost:9200'
    es = Elasticsearch(host)
    index_name = 'qiita'
    with open('./elasticsearch/setting.json') as f:
        print('Load settings.')
        setting = json.load(f)
    with open('./elasticsearch/mapping.json') as f:
        print('Load mappings.')
        mapping = json.load(f)
    if es.indices.exists(index=index_name):
        print('Index exists. Deleted.')
        es.indices.delete(index_name)
    print('Create index.')
    create_index(index_name, mapping, setting)
    print(es.indices.get(index_name))
    # bulkインサート
    print('Insert start.')
    t0 = time.time()
    # helpers.bulk(es, actions=load_data(), chunk_size=1000, timeout=100)
    for data in load_data2():
        helpers.bulk(es, actions=data, request_timeout=100)
    t1 = time.time()
    elapsed_time = float(t1 - t0)
    print('Done.')
    print(elapsed_time)


if __name__ == '__main__':
    main()
