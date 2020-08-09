import json
from glob import glob
# from pyknp import Juman
import settings
import os
from os import path, makedirs
import subprocess


def split_into_words(text):
    text_list = split_into_specific_byte(text)

    results = []
    for t in text_list:
        print(f'cmd: echo "{t}"| jumanpp')
        cmd = subprocess.run(f'echo "{t}"| jumanpp', encoding='utf-8', stdout=subprocess.PIPE, shell=True)
        # cmd = subprocess.run(f'echo "{t}"| jumanpp', stdout=subprocess.PIPE, shell=True)
        res = [r.split()[0] for r in cmd.stdout.decode('utf-8').splitlines()]
        results.append(res)
    result = []
    for r in results:
        result.extend(r[:-1])
    return result


def split_into_specific_byte(input_str, split_byte=4000):
    print(f'input: {len(input_str.encode("utf-8"))}')

    result = []
    while True:
        if input_str == '':
            break
        sample_str = input_str
        while len(sample_str.encode('utf-8')) > split_byte:
            sample_str = sample_str[:-1]
        result.append(sample_str)
        input_str = input_str[len(sample_str):]
    return result


def doc_to_sentence(doc):
    doc = replace_all(
        doc,
        {
            '\n': '',
            '\'': '’',
            '`': '｀',
            '"': '”',
            '@': '＠',
            '#': '＃',
            ' ': '',  # 半角スペース
            '　': '',  # 全角スペース
            '<': '＜',
            '>': '＞',
            '|': '｜',
            '(': '（',
            ')': '）',
            '&': '＆',
            '%': '％',
            '\\': '＼',
            '-': 'ー'
        }
    )
    return split_into_words(doc)


def replace_all(input_str='', replaces=None):
    if replaces is not None:
        for from_, to in replaces.items():
            input_str = input_str.replace(from_, to)
    return input_str


def load_data():
    data_path = path.join(settings.doc_data_dir, '*.json')
    print(f'data_path: {data_path}')
    for d in glob(data_path, recursive=True):
        print(f'Load json: {d}')

        with open(d, encoding='utf-8') as f:
            monthly_data = json.load(f)
            for data in monthly_data:
                yield data['body']


def sentence_generator():
    for i, doc in enumerate(load_data()):
        if i > 10:
            break
        print(f'count: {i + 1}')
        yield ' '.join(doc_to_sentence(doc)) + '\n'
    print()


def main():
    data_path = path.join(settings.sentences_data_dir, settings.sentences_data_name)
    makedirs(settings.sentences_data_dir, exist_ok=True)

    if os.name == 'nt':
        subprocess.call('chcp 65001', stdout=subprocess.PIPE, shell=True)

    with open(data_path, mode='w', encoding='utf-8') as f:
        f.writelines(sentence_generator())


if __name__ == '__main__':
    main()
