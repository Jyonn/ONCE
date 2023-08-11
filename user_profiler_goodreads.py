import json
import time

from tqdm import tqdm

from processor.goodreads.prompter import GoodreadsPrompter, GoodreadsUser
from utils.openai.chat_service import ChatService

MIN_INTERVAL = 0

# concise

goodreads_prompter = GoodreadsPrompter('data/goodreads/book.csv', desc_path='data/goodreads/book-desc.csv')
user_list = GoodreadsUser('data/goodreads/user', goodreads_prompter).stringify()

system = """You are asked to describe user interest based on his/her browsed news list, the format of which is as below:

(1) {book title}, description: {book desc}
...
(n) {book title}, description: {book desc}

You can only response the user interests (at most 5 words) in JSON format:

{
    "interests": [...]
}

where each interest should be a single word. You are not allowed to response any other words for any explanation or note. Now, the task formally begins. Any other information should not disturb you."""

save_path = 'data/goodreads/user_profiler.log'

with open(save_path, 'a') as f:
    pass

exist_set = set()
with open(save_path, 'r') as f:
    for line in f:
        data = json.loads(line)
        exist_set.add(data['uid'])

print('exist count: ', len(exist_set))
empty_count = 0

for uid, content in tqdm(user_list):
    start_time = time.time()
    if uid in exist_set:
        continue

    if not content:
        empty_count += 1
        continue

    enhanced = ''

    try:
        service = ChatService(system)
        enhanced = service.ask(content)  # type: str
        enhanced = enhanced.rstrip('\n')

        interest = json.loads(enhanced)['interests']

        with open(save_path, 'a') as f:
            f.write(json.dumps({'uid': uid, 'interest': interest}) + '\n')
    except Exception as e:
        print(e)
        print(uid, enhanced)

    interval = time.time() - start_time
    if interval <= MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - interval)

print('empty count: ', empty_count)
