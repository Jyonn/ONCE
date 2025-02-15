# MIND Processor for LegommendersV2

The released processing data is not fully compatible to the LegommendersV2.
This new folder is used to process the data using UniTokV4 and the new LegommendersV2.

## Installation

```bash
pip install -U unitok
pip install -U smartdict
```

Make sure you are using the latest version of the Legommenders:

```bash
git clone https://github.com/Jyonn/Legommenders
```

## Usage

### STEP 1: Copy files

1. copy processor/once_mind_processor.py to Legommenders/processor/once_mind_processor.py
2. copy processor/mind_imp_list.json to Legommenders/mind_imp_list.json

### STEP 2: Download the original MIND-small dataset

Website: https://msnews.github.io/

### STEP 3: Unzip the original MIND-small dataset

The MIND folder should be constructed as follows:

```text
/path/to/MIND
├── dev
│   ├── behaviors.tsv
│   └── news.tsv
├── train
│   ├── behaviors.tsv
│   └── news.tsv
```

### STEP 4: Config the dataset path

Add new file `.data` in the Legommenders folder:

```text
oncemind = /path/to/MIND$mind_imp_list.json
```

The path before `$` is the path to the MIND folder, and the path after `$` is the path to the `mind_imp_list.json` file.

### STEP 5: Prepare the GloVe vocabulary in the Legommenders folder

```bash
python embed.py --model glove
```

### STEP 6: Process the MIND dataset in the Legommenders folder using the processor

```bash
python process.py --dataset oncemind
```

### STEP 7: Set the MIND data config in `config/data/oncemind.yaml`

```yaml
name: oncemind
base_dir: data/oncemind
item:
  ut: ${data.base_dir}/items
  inputs:
    - title@glove: 30
    - category
user:
  ut: ${data.base_dir}/users
  truncate: 50
inter:
  train: ${data.base_dir}/train
  dev: ${data.base_dir}/valid
  test: ${data.base_dir}/test
  filters:
    history:
      - "lambda x: x"
column_map:
  item_col: item_id
  user_col: user_id
  history_col: history
  neg_col: neg
  label_col: click
  group_col: user_id
```

You can also prepare `oncemind-lm.yaml` and `oncemind-lm-prompt.yaml` based on the `mind-lm.yaml` and `mind-lm-prompt.yaml`.

### STEP 8: Train the model

```bash
python trainer.py --data config/data/oncemind.yaml --model config/model/naml.yaml --batch_size 64 --lr 0.001
```

Logs:

```text
[00:00:22] |Trainer| use single lr: 0.001
[00:00:22] |Trainer| embedding_vocab_table.glove.weight torch.Size([400000, 256])
[00:00:22] |Trainer| embedding_vocab_table.category.weight torch.Size([18, 256])
[00:00:22] |Trainer| item_op.cnn.weight torch.Size([256, 256, 3])
[00:00:22] |Trainer| item_op.cnn.bias torch.Size([256])
[00:00:22] |Trainer| item_op.linear.weight torch.Size([256, 256])
[00:00:22] |Trainer| item_op.linear.bias torch.Size([256])
[00:00:22] |Trainer| item_op.additive_attention.encoder.0.weight torch.Size([256, 256])
[00:00:22] |Trainer| item_op.additive_attention.encoder.0.bias torch.Size([256])
[00:00:22] |Trainer| item_op.additive_attention.encoder.2.weight torch.Size([1, 256])
[00:00:22] |Trainer| user_op.additive_attention.encoder.0.weight torch.Size([256, 256])
[00:00:22] |Trainer| user_op.additive_attention.encoder.0.bias torch.Size([256])
[00:00:22] |Trainer| user_op.additive_attention.encoder.2.weight torch.Size([1, 256])
[00:03:50] |BaseLego| [epoch 0] GAUC 0.6159                           
[00:03:52] |Trainer| save model to checkpoints/oncemind/NAML/B-Mi20aL.pt
[00:07:15] |BaseLego| [epoch 1] GAUC 0.6323                           
[00:07:19] |Trainer| save model to checkpoints/oncemind/NAML/B-Mi20aL.pt
[00:10:38] |BaseLego| [epoch 2] GAUC 0.6349                           
[00:10:42] |Trainer| save model to checkpoints/oncemind/NAML/B-Mi20aL.pt
[00:13:50] |BaseLego| [epoch 3] GAUC 0.6402                           
[00:13:54] |Trainer| save model to checkpoints/oncemind/NAML/B-Mi20aL.pt
[00:17:06] |BaseLego| [epoch 4] GAUC 0.6287                           
[00:19:53] |BaseLego| [epoch 5] GAUC 0.6237                           
[00:22:57] |BaseLego| [epoch 6] GAUC 0.6096                           
[00:26:15] |BaseLego| [epoch 7] GAUC 0.6149                           
[00:29:15] |BaseLego| [epoch 8] GAUC 0.5965           
[00:29:15] |Trainer| Early stop
[00:29:15] |Trainer| Training Ended
[00:29:16] |Trainer| load model from checkpoints/oncemind/NAML/B-Mi20aL.pt
/home/data1/qijiong/Code/Legommenders/utils/metrics.py:179: UserWarning: Following existing recommendation repositories, the implementation of MRR is not the same as the original one. To get the original MRR, use MRR0 instead.
  warnings.warn('Following existing recommendation repositories, '
[00:31:33] |Trainer| GAUC: 0.6387     
[00:31:33] |Trainer| MRR: 0.2750
[00:31:33] |Trainer| NDCG@1: 0.1754
[00:31:33] |Trainer| NDCG@5: 0.3039
[00:31:33] |Trainer| NDCG@10: 0.3652
```