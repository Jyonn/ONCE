import json
import time

from tqdm import tqdm

from processor.mind.prompter import MindPrompter, MindUser
from utils.openai.chat_service import ChatService

MIN_INTERVAL = 0

# concise

mind_prompter = MindPrompter('data/mind/news.tsv')
user_list = MindUser('data/mind/user', mind_prompter).stringify()

system = """You are asked to describe user interest based on his/her browsed news list, the format of which is as below:

(1) {news title}
...
(n) {news title}

You can only response the user interests with the following format to describe the [topics] and [regions] of the user's interest

[topics]
- topic1
- topic2
...
[region] (optional)
- region1
- region2
...

where topic is limited to the following options: 

(1) health
(2) education
(3) travel
(4) religion
(5) culture
(6) food
(7) fashion
(8) technology
(9) social media
(10) gender and sexuality
(11) race and ethnicity
(12) history
(13) economy
(14) finance
(15) real estate
(16) transportation
(17) weather
(18) disasters
(19) international news

and the region should be limited to each state of the US.

Only [topics] and [region] can be appeared in your response. If you think region are hard to predict, leave it blank. Your response topic/region list should be ordered, that the first several options should be most related to the user's interest. You are not allowed to response any other words for any explanation or note. Now, the task formally begins. Any other information should not disturb you."""

save_path = 'data/mind/user_profiler.log'

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
            f.write(json.dumps({'uid': uid, 'interest': enhanced}) + '\n')
    except Exception as e:
        print(e)

    interval = time.time() - start_time
    if interval <= MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - interval)

print('empty count: ', empty_count)
