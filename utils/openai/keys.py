class Keys:
    def __init__(self, apikey=None):
        if apikey:
            self.apikeys = [apikey]
        else:
            self.apikeys = open('.openai').read().split('\n')
        self.current_apikey = 0
        print(f'total {len(self.apikeys)} keys')

    def get_apikey(self):
        apikey = self.apikeys[self.current_apikey]
        self.current_apikey = (self.current_apikey + 1) % len(self.apikeys)
        return apikey
