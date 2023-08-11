import pandas as pd
from UniTok import Vocab, UniTok, Column
from UniTok.tok import IdTok, BertTok, BaseTok
from transformers import LlamaTokenizer

save_path = 'data/goodreads/book_summarizer.log'


class LlamaTok(BaseTok):
    return_list = True

    def __init__(self, name, vocab_dir):
        super(LlamaTok, self).__init__(name=name)
        self.tokenizer = LlamaTokenizer.from_pretrained(pretrained_model_name_or_path=vocab_dir)
        vocab = [self.tokenizer.convert_ids_to_tokens(i) for i in range(self.tokenizer.vocab_size)]
        self.vocab.extend(vocab)

    def t(self, obj) -> [int, list]:
        if pd.notnull(obj):
            ts = self.tokenizer.tokenize(obj)
            ids = self.tokenizer.convert_tokens_to_ids(ts)
        else:
            ids = []
        return ids


df = pd.read_csv(
    filepath_or_buffer='data/goodreads/book-desc.csv',
    sep=',',
    header=0,
)

vocab = Vocab('bid').load('data/goodreads/user')
id_tok = IdTok(name='bid')
id_tok.vocab = vocab
UniTok().add_col(Column(
    name='bid',
    tok=id_tok,
)).add_col(Column(
    name='desc',
    tok=LlamaTok(name='llama', vocab_dir='llama-tokenizer'),
    max_length=50,
)).read(df).tokenize().store('goodreads-desc-llama')
