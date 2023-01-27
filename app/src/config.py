import os


class Config:
    def __init__(self) -> None:
        if os.environ.get('BOT_API_KEY') is None:
            raise EnvironmentError('BOT_API_KEY was not found')
        self.api_key: str = os.environ['BOT_API_KEY']
