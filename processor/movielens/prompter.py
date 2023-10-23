import json
import os

import pandas as pd
from UniTok import UniDep
from tqdm import tqdm


class MovieLensPrompter:
    def __init__(self, data_path, desc_path=None, v2=False):
        self.data_path = data_path
        self.desc_path = desc_path
        self.v2 = v2

        self.movie_df = pd.read_csv(
            filepath_or_buffer=os.path.join(data_path),
            sep=',',
            header=0,
        )
        print(len(self.movie_df))

        self.use_desc = desc_path is not None
        if desc_path:
            self.desc_df = pd.read_csv(
                filepath_or_buffer=os.path.join(desc_path),
                sep=',',
                header=0,
            )
            print(len(self.desc_df))
            self.movie_df = pd.merge(self.movie_df, self.desc_df, on='mid')
            print(len(self.movie_df))

        self._movie_list = None
        self._movie_dict = None

    def stringify(self):
        if self._movie_list is not None:
            return self._movie_list
        self._movie_list = []
        for movie in tqdm(self.movie_df.iterrows()):
            if self.use_desc:
                if self.v2:
                    string = f'name: {movie[1]["name"]}\ndescription: {movie[1]["desc"]}\n'
                else:
                    string = f'[movie] {movie[1]["name"]}, description: {movie[1]["description"]}\n'
            else:
                string = f'[movie] {movie[1]["name"]}\n'
            self._movie_list.append((str(movie[1]['mid']), string))
        return self._movie_list

    def get_movie_dict(self):
        if self._movie_dict is not None:
            return self._movie_dict
        self._movie_dict = {}
        for news in tqdm(self.movie_df.iterrows()):
            mid = str(news[1]['mid'])
            desc = ' '.join(news[1]["desc"].split(' ')[:50])
            if self.use_desc:
                self._movie_dict[mid] = f'{news[1]["name"]}, description: {desc}'
            else:
                self._movie_dict[mid] = news[1]['title']
        return self._movie_dict


class MovieLensUser:
    def __init__(self, data_path, goodreads_prompter: MovieLensPrompter):
        self.depot = UniDep(data_path, silent=True)
        self.mid = self.depot.vocabs('mid')
        self.movie_dict = goodreads_prompter.get_movie_dict()

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
                string += f'({i + 1}) {self.movie_dict[self.mid.i2o[n]]}\n'
            self._user_list.append((user['uid'], string))
        return self._user_list


class MovieLensColdUser:
    def __init__(self, data_path, goodreads_prompter: MovieLensPrompter):
        self.depot = UniDep(data_path, silent=True)
        self.mid = self.depot.vocabs('mid')
        self.movie = goodreads_prompter.get_movie_dict()

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
                string += f'({i + 1}) {self.movie[self.mid.i2o[n]]}\n'
            self._user_list.append((user['uid'], string))
        return self._user_list


class MovieLensCoT:
    def __init__(self, data_path, profile_path, goodreads_prompter: MovieLensPrompter):
        self.depot = UniDep(data_path, silent=True)

        self.topics = dict()
        with open(profile_path, 'r') as f:
            for line in f:
                if line.endswith('\n'):
                    line = line[:-1]
                data = json.loads(line)
                uid, topic = data['uid'], data['interest']
                self.topics[uid] = topic
        self.mid = self.depot.vocabs('mid')
        self.movie_dict = goodreads_prompter.get_movie_dict()

        self._user_list = None

    def stringify(self):
        if self._user_list is not None:
            return self._user_list
        self._user_list = []
        for user in tqdm(self.depot):
            string = ''
            pg = self.topics[user['uid']]
            string += 'Interest Topics:\n'
            for t in pg:
                string += f'- {t}\n'
            string += '\n'

            string += 'History:\n'
            for i, n in enumerate(user['history']):
                string += f'({i + 1}) {self.movie_dict[self.mid.i2o[n]]}\n'
            self._user_list.append((user['uid'], string))
        return self._user_list
