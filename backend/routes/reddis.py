/backend/routes/redis.py
import redis

# Connect to Redis
redis_client = redis.Redis(host="localhost", port=6379, db=1, decode_responses=True)



# r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# r.flushdb()  # Clears only the current database
# # or
# r.flushall()  # Clears ALL databases (if using multiple DBs)

# print("Redis database cleared!")

# Get all keys
keys = redis_client.keys("*")
print("Stored keys:", keys)

# Get values for each key
for key in keys:
    value = redis_client.get(key)
    print(f"Key: {key}, Value: {value}")
    
    
    
    
# import redis

# r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# key = "celery-task-meta-f9a0a5f1-dd81-4bcc-93db-bf07051c1456"

# key_type = r.type(key)
# print(f"Key Type: {key_type}")

# if key_type == "hash":
#     value = r.hgetall(key)  # Fetch all fields if it's a hash
# elif key_type == "string":
#     value = r.get(key)
#     if value:
#         import json
#         value = json.loads(value)
# else:
#     value = "Unsupported key type"

# print("Value:", value)
