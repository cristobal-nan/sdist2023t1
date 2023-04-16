import csv
import random
import sys
import asyncio
import aiohttp
import json
import time

from api import handle_query as api_handle_query
from apiCache import handle_query as cache_handle_query

QUERIES = ['python', 'openai', 'machine learning', 'neural networks', 'data science']
QUERIES_PER_WORKER = 100

async def test(num_workers, query_func, queries):
    start_time = time.time()
    results = []
    num_queries = len(queries)
    queries_per_worker = num_queries // num_workers + 1
    queries_per_worker *= 5
    async with asyncio.Semaphore(num_workers):
        coroutines = []
        for i in range(0, num_queries, queries_per_worker):
            worker_queries = queries[i:i+queries_per_worker]
            num_worker_queries = len(worker_queries)
            queries_per_worker_divided = num_worker_queries // num_workers
            for j in range(num_workers):
                start_index = j * queries_per_worker_divided
                end_index = (j + 1) * queries_per_worker_divided
                if j == num_workers - 1:
                    end_index = num_worker_queries
                subqueries = worker_queries[start_index:end_index]
                coroutines.extend([handle_query(query_func, query) for query in subqueries])
        results = await asyncio.gather(*coroutines)
    end_time = time.time()
    return end_time - start_time, results


async def handle_query(query_func, query):
    result = await query_func(query)
    return result

async def main():
    num_workers = 1

    # Run tests for different number of workers
    with open('results.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Workers', 'Query Function', 'Query', 'Time Taken'])
        
        for i in range(1, 11):
            num_workers = i
            print(f'Testing with {num_workers} workers...')
            for query in QUERIES:
                time_taken, results = await test(num_workers, api_handle_query, [query] * 5)
                writer.writerow([num_workers, 'API', query, f'{time_taken / 5:.10f}'])
                total_queries = len([query] * 5)
                
                time_taken, results = await test(num_workers, cache_handle_query, [query] * 5)
                writer.writerow([num_workers, 'Cache', query, f'{time_taken / 5:.10f}'])
                total_queries += len([query] * 5)
                
                print(f'Time taken for {query} queries: {time_taken / 5:.10f} seconds')
                
            print(f'Total queries with {num_workers} workers: {total_queries}\n')


if __name__ == '__main__':
    asyncio.run(main())
