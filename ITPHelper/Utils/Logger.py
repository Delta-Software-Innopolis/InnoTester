import aiofiles
from datetime import datetime


class Logger:
    def __init__(self, filename):
        self.filename = filename

    async def info(self, message):
        async with aiofiles.open(self.filename, mode='a') as f:
            await f.write(f"[{datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}] " + message + "\n")
