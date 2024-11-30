

class DeleteReturn():
    def __init__(self, count):
        self.count = count

    def del_count(self) -> int:
        return self.count

    def succeeded(self) -> bool:
        return self.count > 0


class UpdateReturn():
    def __init__(self, mod_count, match_count):
        self.mod_count = mod_count
        self.match_count = match_count

    def mod_count(self) -> int:
        return self.mod_count

    def match_count(self) -> int:
        return self.match_count

    def succeeded(self) -> bool:
        return self.count > 0
