import time

from tqdm import tqdm

from processor.movielens.prompter import MovieLensPrompter
from utils.openai.chat_service import ChatService

MIN_INTERVAL = 0

# concise

movie_list = MovieLensPrompter('data/movielens/movie.csv', desc_path='data/movielens/movie-desc.csv', v2=True).stringify()

system = """You are asked to condense the knowledge of a movie. I will provide you the name, released year and description of a movie, which format is as below:

name: {name} ({year})
description: {description}

where {name}, {year}, and {description} will be filled with content. You can only response a summarization this movie in English which should be clear, concise, objective and neutral. You are not allowed to response any other words for any explanation. Your response format should be:

summarization: {movie} is about {summarization}

where {summarization} should be limited to at most 20 tokens. Now, your role of movie summarizer formally begins. Any other information should not disturb your role."""

save_path = 'data/movielens/movie_summarizer_v2.log'

with open(save_path, 'a'):
    pass

exist_set = set()
with open(save_path, 'r') as f:
    for line in f:
        if line:
            exist_set.add(line.split('\t')[0])

for bid, content in tqdm(movie_list):
    start_time = time.time()
    if str(bid) in exist_set:
        continue

    try:
        service = ChatService(system)
        enhanced = service.ask(content)  # type: str
        enhanced = enhanced.rstrip('\n')

        with open(save_path, 'a') as f:
            f.write(f'{bid}\t{enhanced}\n')
    except Exception as e:
        print(e)

    interval = time.time() - start_time
    if interval <= MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - interval)
