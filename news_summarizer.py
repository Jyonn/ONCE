import time

from tqdm import tqdm

from processor.mind.prompter import MindPrompter
from utils.openai.chat_service import ChatService

MIN_INTERVAL = 1.5

# concise

news_list = MindPrompter('data/mind/news.tsv').stringify()
system = """You are asked to act as a news title enhancer. I will provide you a piece of news, with its original title, category, subcategory, and abstract (if exists). The news format is as below:

[title] {title}
[abstract] {abstract}
[category] {category}
[subcategory] {subcategory}

where {title}, {abstract}, {category}, and {subcategory} will be filled with content. You can only response a rephrased news title which should be clear, complete, objective and neutral. You can expand the title according to the above requirements. You are not allowed to response any other words for any explanation. Your response format should be:

[newtitle] {newtitle}

where {newtitle} should be filled with the enhanced title. Now, your role of news title enhancer formally begins. Any other information should not disturb your role."""


save_path = 'data/mind/enhanced.log'

exist_set = set()
with open(save_path, 'r') as f:
    for line in f:
        if line and line.startswith('N'):
            exist_set.add(line.split('\t')[0])


for nid, content in tqdm(news_list):
    start_time = time.time()
    if nid in exist_set:
        continue

    try:
        service = ChatService(system)
        enhanced = service.ask(content)  # type: str
        enhanced = enhanced.rstrip('\n')

        with open(save_path, 'a') as f:
            f.write(f'{nid}\t{enhanced}\n')
    except Exception as e:
        print(e)

    interval = time.time() - start_time
    if interval <= MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - interval)
