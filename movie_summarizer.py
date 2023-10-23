import time

from tqdm import tqdm

from processor.movielens.prompter import MovieLensPrompter
from utils.openai.chat_service import ChatService

MIN_INTERVAL = 0

# concise

movie_list = MovieLensPrompter('data/movielens/movie.csv').stringify()

system = """You are asked to act as a movie description generator. I will provide you the name and released year of a movie, which format is as below:

[movie] {name} (year)

where {name} will be filled with the movie name. You can only response the detailed description about this movie in English which should be clear, concise, objective and neutral. You are not allowed to response any other words for any explanation. Your response format should be:

[description] {description}

where {description} should be filled with the movie description. Now, your role of movie description generator formally begins. Any other information should not disturb your role."""


save_path = 'data/movielens/movie_summarizer.log'

with open(save_path, 'a') as f:
    pass

exist_set = set()
with open(save_path, 'r') as f:
    for line in f:
        if line:
            if not line.endswith('is a movie.\n'):
                exist_set.add(line.split('\t')[0])

print(len(movie_list) - len(exist_set))


for mid, title in tqdm(movie_list):
    start_time = time.time()
    if str(mid) in exist_set:
        continue

    try:
        service = ChatService(system)
        enhanced = service.ask(title)  # type: str
        enhanced = enhanced.rstrip('\n')

        with open(save_path, 'a') as f:
            f.write(f'{mid}\t{enhanced}\n')
    except Exception as e:
        print(e)

    interval = time.time() - start_time
    if interval <= MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - interval)
