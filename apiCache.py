import sys
import asyncio
import aiohttp
import json
import time
import redis

# API endpoint for DuckDuckGo Instant Answer API
API_ENDPOINT = 'https://api.duckduckgo.com/'

# Cache dictionary to store query results
cache = {}

# Connect to Redis using docker-compose configuration
redis_connection_pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    decode_responses=True,
    db=0
)
redis_db = redis.Redis(connection_pool=redis_connection_pool)

# Asynchronous function to query the API or retrieve from cache
async def query_api(query):
    if query in cache:
        return cache[query]
    params = {
        'q': query,
        'format': 'json',
        'no_redirect': 1
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(API_ENDPOINT, params=params) as resp:
            response = await resp.text()
            result = json.loads(response)
            cache[query] = result
            redis_db.set(query, json.dumps(result))
            return result

# Asynchronous function to handle user query
async def handle_query(query):
    redis_result = redis_db.get(query)
    if redis_result is not None:
        result = json.loads(redis_result)
        cache[query] = result
        return result
    result = await query_api(query)
    return result

# Main function to run the system
async def main():
    if len(sys.argv) < 2:
        print('Usage: python3 apiCache.py <query>')
        return
    query = ' '.join(sys.argv[1:])
    result = await handle_query(query)
    print(result)

if __name__ == '__main__':
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f'Time taken: {end_time - start_time:.2f} seconds')