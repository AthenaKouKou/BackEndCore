

class DeleteReturn():
    def __init__(self, count):
        self.deleted_count = count

    def del_count(self) -> int:
        return self.deleted_count

    def succeeded(self) -> bool:
        return self.deleted_count > 0


class UpdateReturn():
    def __init__(self, mod_count, match_count):
        self.modified_count = mod_count
        self.matched_count = match_count

    def mod_count(self) -> int:
        return self.modified_count

    def match_count(self) -> int:
        return self.matched_count

    def succeeded(self) -> bool:
        return self.matched_count > 0
