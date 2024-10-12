# Pretty sure i don't use this anywhere 10/12/24
class NoVideoFoundError(Exception):
    def __init__(self, message="No video found. 🧪🧪🧪🧪🧪"):
        self.message = message
        super().__init__(self.message)
