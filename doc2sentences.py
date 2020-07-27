import json
from glob import glob
from pyknp import Juman
import settings
from os import path, makedirs


def load_data():
    data_path = path.join(settings.doc_data_dir, '*.json')
    print(f'data_path: {data_path}')
    for d in glob(data_path, recursive=True):
        print(f'Load json: {d}')

        with open(d, encoding='utf-8') as f:
            monthly_data = json.load(f)
            for data in monthly_data:
                yield data['body']


def split_into_words(text):
    #  4096バイト以下の文字列になるまで分割する
    _list = [text]
    br = False
    while True:
        if br:
            break
        for t in _list:
            if not len(t.encode('utf-8')) > 4096:
                br = True
                break
            # 過去の分割は捨てる
            _list = _list[:1]
            # 適当に半分にして再度バイト数チェックに回す
            _list.append(t[:len(t) // 2])
            _list.append(t[len(t) // 2:])

    results = []
    if len(_list) > 1:
        for t in _list[1:]:
            results.append(Juman().analysis(t))
        result = ''
        for r in results:
            result = [mrph.midasi for mrph in r.mrph_list()]
    else:
        result = [mrph.midasi for mrph in Juman().analysis(_list[0])]
    return result


def doc_to_sentence(doc):
    doc = replace_all(
        doc,
        {
            '\n': '',
            '\'': '’',
            '"': '”',
            '@': '＠',
            '#': '＃',
            ' ': '　'
        }
    )
    return split_into_words(doc)


def replace_all(input_str='', replaces=None):
    if replaces is not None:
        for from_, to in replaces.items():
            input_str = input_str.replace(from_, to)
    return input_str


def sentence_generator():
    for i, doc in enumerate(load_data()):
        print(f'\rcount: {i + 1}', end='')
        yield ' '.join(doc_to_sentence(doc)) + '\n'
    print()


def main():
    data_path = path.join(settings.sentences_data_dir, 'sentences.cor')
    makedirs(settings.sentences_data_dir, exist_ok=True)

    with open(data_path, mode='w', encoding='utf-8') as f:
        f.writelines(sentence_generator())


if __name__ == '__main__':
    main()
