import json
import os

import pandas as pd
from UniTok import UniDep
from tqdm import tqdm


class GoodreadsPrompter:
    def __init__(self, data_path, desc_path=None):
        self.data_path = data_path
        self.desc_path = desc_path

        self.book_df = pd.read_csv(
            filepath_or_buffer=os.path.join(data_path),
            sep='\t',
            header=0,
        )

        self.use_desc = desc_path is not None
        if desc_path:
            self.desc_df = pd.read_csv(
                filepath_or_buffer=os.path.join(desc_path),
                sep=',',
                header=0,
            )
            self.book_df = pd.merge(self.book_df, self.desc_df, on='bid')

        self._book_list = None
        self._book_dict = None

    def stringify(self):
        if self._book_list is not None:
            return self._book_list
        self._book_list = []
        for news in tqdm(self.book_df.iterrows()):
            if self.use_desc:
                string = f'[book] {news[1]["title"]}, description: {news[1]["description"]}\n'
            else:
                string = f'[book] {news[1]["title"]}\n'
            self._book_list.append((str(news[1]['bid']), string))
        return self._book_list

    def get_book_dict(self):
        if self._book_dict is not None:
            return self._book_dict
        self._book_dict = {}
        for news in tqdm(self.book_df.iterrows()):
            bid = str(news[1]['bid'])
            desc = ' '.join(news[1]["desc"].split(' ')[:50])
            if self.use_desc:
                self._book_dict[bid] = f'{news[1]["title"]}, description: {desc}'
            else:
                self._book_dict[bid] = news[1]['title']
        return self._book_dict


class GoodreadsUser:
    def __init__(self, data_path, goodreads_prompter: GoodreadsPrompter):
        self.depot = UniDep(data_path, silent=True)
        self.bid = self.depot.vocabs('bid')
        self.book_dict = goodreads_prompter.get_book_dict()

        self._user_list = None

    def stringify(self):
        if self._user_list is not None:
            return self._user_list
        self._user_list = []
        for user in tqdm(self.depot):
            string = ''
            if not user['history']:
                self._user_list.append((user['uid'], None))
            for i, n in enumerate(user['history']):
                string += f'({i + 1}) {self.book_dict[self.bid.i2o[n]]}\n'
            self._user_list.append((user['uid'], string))
        return self._user_list


class GoodreadsColdUser:
    def __init__(self, data_path, goodreads_prompter: GoodreadsPrompter):
        self.depot = UniDep(data_path, silent=True)
        self.bid = self.depot.vocabs('bid')
        self.book = goodreads_prompter.get_book_dict()

        self._user_list = None

    def stringify(self):
        if self._user_list is not None:
            return self._user_list
        self._user_list = []
        for user in tqdm(self.depot):
            string = ''
            if not user['history'] or len(user['history']) > 5:
                continue
            for i, n in enumerate(user['history']):
                string += f'({i + 1}) {self.book[self.bid.i2o[n]]}\n'
            self._user_list.append((user['uid'], string))
        return self._user_list


class GoodreadsCoT:
    def __init__(self, data_path, plugin_path, goodreads_prompter: GoodreadsPrompter, allowed_user_path):
        self.depot = UniDep(data_path, silent=True)
        self.plugin = UniDep(plugin_path, silent=True)
        self.tv = self.plugin.vocabs['topic']
        self.rv = self.plugin.vocabs['region']

        self.bid = self.depot.vocabs('bid')
        self.book_dict = goodreads_prompter.get_book_dict()

        self._user_list = None
        self.allowed_user = json.load(open(allowed_user_path))

    def stringify(self):
        if self._user_list is not None:
            return self._user_list
        self._user_list = []
        for user in tqdm(self.depot):
            if user['uid'] not in self.allowed_user:
                continue
            string = ''
            pg = self.plugin[user['uid']]
            string += 'Interest Topics:\n'
            for t in pg['topic']:
                string += f'- {self.tv[t]}\n'
            string += '\n'
            # string += 'Interest Regions:\n'
            # for r in pg['region']:
            #     string += f'- {self.rv[r]}\n'
            # string += '\n'

            string += 'History:\n'
            for i, n in enumerate(user['history']):
                string += f'({i + 1}) {self.book_dict[self.bid.i2o[n]]}\n'
            self._user_list.append((user['uid'], string))
        return self._user_list
