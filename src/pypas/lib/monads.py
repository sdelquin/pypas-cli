class Monad:
    ERROR = 0
    SUCCESS = 1

    def __init__(self, status: int, payload: object):
        self.status = status
        self.payload = payload

    def __bool__(self):
        return self.status == self.SUCCESS
