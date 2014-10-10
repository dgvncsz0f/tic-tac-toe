import json
import uuid
import redis

class NotFound (Exception):
    pass

def instance ():
    return(redis.Redis())

def create (db):
    k = str(uuid.uuid4())
    db.setex(k, "", 3600)
    return(k)

def update (db, k, v):
    uuid.UUID(k)
    db.setex(k, json.dumps(v), 3600)

def select (db, k):
    v = db.get(k)
    if v is None:
        raise NotFound
    elif v == "":
        return None
    else:
        return json.loads(v)
