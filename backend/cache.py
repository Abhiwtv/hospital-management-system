import redis
import json

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

TTL_CONFIG = {
    
    "dashboard:admin":      300,
    "appointments:recent":  60,
    "specializations:list": 1800,
    "patients:list":        30,    
    "doctors:list":         600,   
    "departments:list":     1800,  
    "department:detail":    1800,  
    "doctor:availability:detail":  120, 
}


def get_cache(key):
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None


def set_cache(key, value, ttl=None):
    if ttl is None:
        ttl = TTL_CONFIG.get(key)
        if ttl is None:
            prefix = key.rsplit(':', 1)[0]          
            ttl = TTL_CONFIG.get(f"{prefix}:detail") 
        if ttl is None:
            ttl = 300                         
    redis_client.setex(key, ttl, json.dumps(value))


def delete_cache(key):
    redis_client.delete(key)

def blacklist_token(jti, ttl):
    
    redis_client.setex(f"blacklist:{jti}", ttl, "true")
 
 
def is_token_blacklisted(jti):
    return redis_client.exists(f"blacklist:{jti}") > 0