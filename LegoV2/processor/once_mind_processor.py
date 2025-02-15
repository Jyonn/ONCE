import os
from typing import cast

import pandas as pd
from unitok import JsonHandler

from processor.base_processor import Interactions
from processor.mind_processor import MINDProcessor


class ONCEMINDProcessor(MINDProcessor):
    IMP_COL = 'imp'

    def __init__(self, data_dir=None):
        self.imp_list = None

        if data_dir:
            if '$' not in data_dir:
                raise ValueError('data_dir for ONCEMINDProcessor should use $ to concatenate the data path and the imp path')
            data_dir, imp_path = data_dir.split('$')
            self.imp_list = JsonHandler.load(imp_path)

        super().__init__(data_dir=data_dir)

    def _load_interactions(self, path):
        user_set = set(self.user_df[self.UID_COL].unique())

        interactions = pd.read_csv(
            filepath_or_buffer=cast(str, path),
            sep='\t',
            names=[self.IMP_COL, self.UID_COL, 'time', self.HIS_COL, 'predict'],
            usecols=[self.IMP_COL, self.UID_COL, 'predict']
        )

        interactions = interactions[interactions[self.UID_COL].isin(user_set)]
        interactions['predict'] = interactions['predict'].str.split().apply(
            lambda x: [item.split('-') for item in x]
        )
        interactions = interactions.explode('predict')
        interactions[[self.IID_COL, self.LBL_COL]] = pd.DataFrame(interactions['predict'].tolist(),
                                                                  index=interactions.index)
        interactions.drop(columns=['predict'], inplace=True)
        interactions[self.LBL_COL] = interactions[self.LBL_COL].astype(int)
        return interactions

    def splitter(self, portions: list):
        sum_portions = sum(portions)
        portions = [int(p * len(self.imp_list) / sum_portions) for p in portions]
        portions[-1] = len(self.imp_list) - sum(portions[:-1])

        current_position = 0
        imp_lists = []
        for portion in portions:
            imp_lists.append(self.imp_list[current_position: current_position+portion])
            current_position += portion
        return imp_lists

    def load_interactions(self) -> [pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        train_df = self._load_interactions(os.path.join(self.data_dir, 'train', 'behaviors.tsv'))
        dev_df = self._load_interactions(os.path.join(self.data_dir, 'dev', 'behaviors.tsv'))

        dev_imps, test_imps = self.splitter([5, 5])
        dev_list, test_list = [], []

        groups = dev_df.groupby(self.IMP_COL)
        for imp, imp_df in groups:
            target = dev_list if imp in dev_imps else test_list
            target.append(imp_df)

        valid_df = pd.concat(dev_list, ignore_index=True)
        test_df = pd.concat(test_list, ignore_index=True)

        train_df = train_df.reset_index(drop=True)
        valid_df = valid_df.reset_index(drop=True)
        test_df = test_df.reset_index(drop=True)

        return Interactions(train_df, valid_df, test_df)
