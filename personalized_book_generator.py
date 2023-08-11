import json
import time

from tqdm import tqdm

from processor.goodreads.prompter import GoodreadsPrompter, GoodreadsColdUser
from utils.openai.chat_service import ChatService

MIN_INTERVAL = 0

# concise

goodreads_prompter = GoodreadsPrompter('data/goodreads/book.csv', desc_path='data/goodreads/book-desc.csv')
user_list = GoodreadsColdUser('data/goodreads/user', goodreads_prompter).stringify()

system = """You are asked to capture user's interest based on his/her browsing history, and recommend a book that he/she may be interested. The format of history is as below:

(1) {book title}, description: {book desc}
...
(n) {book title}, description: {book desc}

You can only recommend one book (only one) in the following json format:

{
    "title": ...,
    "description": ..., 
}

The book should be diverse, that is not too similar with the original provided book list. You are not allowed to response any other words for any explanation or note. JUST GIVE ME JSON-FORMAT NEWS. Now, the task formally begins. Any other information should not disturb you."""

save_path = 'data/goodreads/generator_v1.log'

with open(save_path, 'a'):
    pass

exist_set = set()
with open(save_path, 'r') as f:
    for line in f:
        data = json.loads(line)
        exist_set.add(data['uid'])

for uid, content in tqdm(user_list):
    start_time = time.time()
    if uid in exist_set:
        continue

    if not content:
        continue

    print(uid, content)

    try:
        service = ChatService(system)
        enhanced = service.ask(content)  # type: str
        enhanced = enhanced.rstrip('\n')

        with open(save_path, 'a') as f:
            f.write(json.dumps({'uid': uid, 'book': enhanced}) + '\n')
    except Exception as e:
        print(e, uid)

    interval = time.time() - start_time
    if interval <= MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - interval)
