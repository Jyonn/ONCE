import json
import time

from tqdm import tqdm

from processor.mind.prompter import MindPrompter, MindUser
from utils.openai.chat_service import ChatService

MIN_INTERVAL = 0

# concise

mind_prompter = MindPrompter('data/mind/news.tsv')
user_list = MindUser('data/mind/user', mind_prompter).stringify()

system = """Given the browsed news list of a user, you are asked to select most representative ones among the list. The format of the news list is as below:

(1) {news title}
...
(n) {news title}

You can only response five indices of most representative ones. The format is as below:

{
	"selected": [...]
}

Only the "selected" attribute can be appeared in the JSON dict. You are not allowed to response any other words for any explanation or note. Now, the task formally begins. Any other information should not disturb you."""

save_path = 'data/mind/history_compressor.log'

with open(save_path, 'a') as f:
    pass

exist_set = set()
with open(save_path, 'r') as f:
    for line in f:
        data = json.loads(line)
        exist_set.add(data['uid'])

empty_count = 0

for uid, content in tqdm(user_list):
    start_time = time.time()
    if uid in exist_set:
        continue

    if not content:
        empty_count += 1
        continue

    try:
        service = ChatService(system)
        enhanced = service.ask(content)  # type: str
        enhanced = enhanced.rstrip('\n')

        with open(save_path, 'a') as f:
            f.write(f'{uid}\t{enhanced}\n')
    except Exception as e:
        print(e)

    interval = time.time() - start_time
    if interval <= MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - interval)

print('empty count: ', empty_count)
