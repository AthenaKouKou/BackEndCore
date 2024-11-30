

class DeleteReturn():
    @classmethod
    def del_ret_from_mongo(cls, mongo_ret):
        return cls.DeleteReturn(mongo_ret.deleted_count)

    def __init__(self, count):
        self.count = count

    def del_count(self) -> int:
        return self.count

    def succeeded(self) -> bool:
        return self.count > 0
