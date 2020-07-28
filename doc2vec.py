import csv
from os import listdir, path, makedirs
from datetime import datetime
from gensim import models
from gensim.models.doc2vec import TaggedDocument, TaggedLineDocument
import settings


def main():
    source = path.join(settings.sentences_data_dir, settings.sentences_data_name)
    total_examples = sum(1 for line in open(source))
    print(f'total examples: {total_examples}')

    tagged_docs = TaggedLineDocument(source)

    model = models.Doc2Vec(
        tagged_docs,
        dm=0,
        vector_size=300,
        window=15,
        alpha=.025,
        min_alpha=.025,
        min_count=1,
        sample=1e-6
    )

    print('\n訓練開始')
    for epoch in range(20):
        print('Epoch: {}'.format(epoch + 1))
        model.train(tagged_docs, total_examples=total_examples, epochs=model.epochs)
        model.alpha -= (0.025 - 0.0001) / 19
        model.min_alpha = model.alpha

    makedirs('models', exist_ok=True)
    now = datetime.now().strftime('%Y-%m-%dT%H_%M_%S')
    model.save(f'models/{now}.model')


if __name__ == '__main__':
    main()
