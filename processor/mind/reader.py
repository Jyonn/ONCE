import os

import pandas as pd


class MindReader:
    def __init__(self, news_dirs):
        self.news_dirs = news_dirs

    @staticmethod
    def read_news_data(data_dir, mode):
        return pd.read_csv(
            filepath_or_buffer=os.path.join(data_dir, mode, 'news.tsv'),
            sep='\t',
            names=['nid', 'cat', 'subcat', 'title', 'abs', 'url', 'tit_ent', 'abs_ent'],
            usecols=['nid', 'cat', 'subcat', 'title', 'abs'],
        )

    def combine(self):
        news_list = []
        for data_dir in self.news_dirs:
            news_train_df = self.read_news_data(data_dir, 'train')
            news_dev_df = self.read_news_data(data_dir, 'dev')
            news_df = pd.concat([news_train_df, news_dev_df])
            news_df = news_df.drop_duplicates(['nid'])
            news_list.append(news_df)
        news_df = pd.concat(news_list)
        news_df = news_df.drop_duplicates(['nid'])
        return news_df

    def read(self):
        news_df = self.combine()
        news_df.to_csv('news.tsv', sep='\t', index=False)


if __name__ == '__main__':
    # build MIND-small dataset
    r = MindReader(
        news_dirs=['/data1/qijiong/Data/MIND/', '/data1/qijiong/Data/MIND-large/'],
    )
    r.read()
