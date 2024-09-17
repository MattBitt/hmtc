# 9/16/24 who knows if this is used anywhere
class NoVideoFoundError(Exception):
    def __init__(self, message="No video found. 🧪🧪🧪🧪🧪"):
        self.message = message
        super().__init__(self.message)
