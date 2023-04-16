import sys
import asyncio
import aiohttp
import json
import time

# API endpoint for DuckDuckGo Instant Answer API
API_ENDPOINT = 'https://api.duckduckgo.com/'

# Asynchronous function to query the API
async def query_api(query):
    params = {
        'q': query,
        'format': 'json',
        'no_redirect': 1
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(API_ENDPOINT, params=params) as resp:
            response = await resp.text()
            result = json.loads(response)
            
            return result

# Asynchronous function to handle user query
async def handle_query(query):
    result = await query_api(query)
    return result

# Main function to run the system
async def main():
    if len(sys.argv) < 2:
        print('Usage: python3 api.py <query>')
        return
    query = ' '.join(sys.argv[1:])
    result = await handle_query(query)
    print(result)

if __name__ == '__main__':
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f'Time taken: {end_time - start_time:.2f} seconds')
