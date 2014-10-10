import os
import json
import uuid
import redis

class NotFound (Exception):
    pass

def read_env ():
    try:
        with open(os.path.expanduser("~/etc/tictactoe-config.json"), "r") as fh:
            return json.loads(fh.read(1024))
    except IOError:
        return {}

def instance ():
    env = read_env()
    return redis.Redis(db = env.get("REDIS_DB", 0),
                       host = env.get("REDIS_HOST", "127.0.0.1"),
                       port = env.get("REDIS_POST", 6379),
                       password = env.get("REDIS_PASS"))

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
