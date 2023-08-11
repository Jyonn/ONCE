import openai
from timeout_decorator import timeout_decorator

from utils.openai.keys import Keys


class ChatService:
    _keys = Keys()

    def __init__(self, system=None, keys=None):
        self.dialog = []
        self.keys = keys or self._keys
        if system:
            self.dialog.append({"role": "system", "content": system})

    @timeout_decorator.timeout(5)
    def ask(self, question):
        self.dialog.append({"role": "user", "content": question})
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.dialog,
            api_key=self.keys.get_apikey(),
        )
        self.dialog.append(resp['choices'][0]['message'])
        return resp['choices'][0]['message']['content']


if __name__ == '__main__':
    service = ChatService('You are a Chinese poet.')
    print(service.ask('"举头望明月"的下一句是？'))
    print(service.ask('这首诗是？'))
