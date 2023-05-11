import json
import time

from tqdm import tqdm

from processor.mind.prompter import MindPrompter, MindColdUser, MindCoT
from utils.openai.chat_service import ChatService

MIN_INTERVAL = 0

# concise

mind_prompter = MindPrompter('data/mind/news.tsv')
user_list = MindCoT('data/mind/user', 'data/mind/user-plugin', mind_prompter, allowed_user_path='data/mind/cold-V2.json').stringify()

system = """You are asked to capture user's interest based on his/her browsing history and interests. You should generate a piece of news that he/she may be interested. The format is as below:

Interest Topics:
- interest topic 1
...
- interest topic k

History:
(1) (the category of the first news) the title of the first news
...
(n) (the category of the n-th news) the title of the n-th news 

You can only generate a piece of news (only one) in the following json format:

{"title": <title>, "abstract": <news abstract>, "category": <news category>}

where <news category> is limited to the following options:

- lifestyle
- health
- news
- sports
- weather
- entertainment
- autos
- travel
- foodanddrink
- tv
- finance
- movies
- video
- music
- kids
- middleeast
- northamerica
- games

"title", "abstract", and "category" should be the only keys in the json dict. The news should be diverse, that is not too similar with the original provided news list. You can discover topics that users potentially like, and you don't have to completely fit the interested topics. You are not allowed to response any other words for any explanation or note. JUST GIVE ME JSON-FORMAT NEWS. Now, the task formally begins. Any other information should not disturb you."""

save_path = 'data/mind/chain_v6.log'
# if file not exist, create it
with open(save_path, 'a') as f:
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

    try:
        service = ChatService(system)
        enhanced = service.ask(content)  # type: str
        enhanced = enhanced.rstrip('\n')

        with open(save_path, 'a') as f:
            f.write(json.dumps({'uid': uid, 'news': enhanced}) + '\n')
    except Exception as e:
        print(e)

    interval = time.time() - start_time
    if interval <= MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - interval)
