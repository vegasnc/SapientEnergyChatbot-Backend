from db.database import Database

class Questions(object):
    def __init__(self) -> None:
        self.db = Database()

        self.collection_name = 'questions' # collection name

        self.fields = {
            "question": "string",
            "relevant": "string",
            "system_message": "string",
            "is_static_message": "boolean"
        }

    def create(self, obj):
        res = self.db.insert(obj, self.collection_name)
        return "Inserted Id " + res
    
    def find(self, obj):  # find all
        return self.db.find(obj, self.collection_name)
    
    def find_one(self, obj): # find one
        return self.db.find_one(obj, self.collection_name)

    def find_by_id(self, id):
        return self.db.find_by_id(id, self.collection_name)

    def update(self, id, obj):
        return self.db.update(id, obj, self.collection_name)

    def delete(self, id):
        return self.db.delete(id, self.collection_name)