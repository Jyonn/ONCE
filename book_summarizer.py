import time

from tqdm import tqdm

from processor.goodreads.prompter import GoodreadsPrompter
from utils.openai.chat_service import ChatService

MIN_INTERVAL = 0

# concise

book_list = GoodreadsPrompter('data/goodreads/book.csv').stringify()

system = """You are asked to act as a book description generator. I will provide you the title of a book, which format is as below:

[book] {title}

where {title} will be filled with content. You can only response the description of this book in English which should be clear, concise, objective and neutral. You are not allowed to response any other words for any explanation. Your response format should be:

[description] {description}

where {description} should be filled with the book description. Now, your role of book description generator formally begins. Any other information should not disturb your role."""


save_path = 'data/goodreads/book_summarizer.log'

with open(save_path, 'a') as f:
    pass

exist_set = set()
with open(save_path, 'r') as f:
    for line in f:
        if line:
            if not line.endswith('is a book.\n'):
                exist_set.add(line.split('\t')[0])

print(len(book_list) - len(exist_set))


for bid, title in tqdm(book_list):
    start_time = time.time()
    if str(bid) in exist_set:
        continue

    try:
        service = ChatService(system)
        enhanced = service.ask(title)  # type: str
        enhanced = enhanced.rstrip('\n')

        with open(save_path, 'a') as f:
            f.write(f'{bid}\t{enhanced}\n')
    except Exception as e:
        print(e)

    interval = time.time() - start_time
    if interval <= MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - interval)
