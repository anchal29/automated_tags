import re
from string import punctuation

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import CountVectorizer


"""
Simple identity function works as a passthrough.
"""
def identity(arg):
    return arg

class ItemSelector(BaseEstimator, TransformerMixin):
    """Selects the subset of data i.e. either title or body or code with respect to
        the porvided key.
        >> data = {'a': [1, 5, 2, 5, 2, 8],
                   'b': [9, 4, 1, 4, 1, 3]}
        >> ds = ItemSelector(key='a')
        >> data['a'] == ds.transform(data)
    """
    def __init__(self, keys):
        self.keys = keys

    def fit(self, x, y=None):
        return self

    def transform(self, data_dict):
        if len(self.keys) is 1:
            return data_dict[self.keys[0]]
        combined = []
        for index in range(0, len(data_dict['body'])):
            combined.append(data_dict['body'][index] + '\n' + data_dict['title'][index])
        # print combined
        return combined

class tagCountExtractor(CountVectorizer):
    """Extract the tag count from title and body of the question.

    Takes the complete dictionary of data and finds tag count for each question.
    """
    def __init__(self, **init_params):
        init_params['tokenizer'] = tokenizer
        init_params['token_pattern'] = r'\b\w+\b'
        super(tagCountExtractor, self).__init__(**init_params)

    def fit(self, x, y=None):
        return self

    def transform(self, x):
        return super(tagCountExtractor, self).transform(x)


tag_re = '[' + punctuation.replace('#', '').replace('+', '').replace('_', '').replace('-', '') + ']+'
tag_re = re.compile(tag_re)

def tokenizer(s):
    return tag_re.sub(' ', s).split()
