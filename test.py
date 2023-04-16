import csv
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor

# Number of requests per worker
REQUESTS_PER_WORKER = 1

# List of worker counts to test
WORKER_COUNTS = list(range(1, 11))

# Query to search for
QUERY = 'sistemas'

# File to export results to
RESULTS_FILE = 'api_results.csv'

# Function to run the API program and measure the execution time
def run_api_program(program, query):
    start_time = time.time()
    output = subprocess.check_output(f'{program} "{query}"', shell=True).decode()
    end_time = time.time()
    execution_time = end_time - start_time
    return (output.strip(), execution_time)

# Function to run multiple API requests in parallel
def run_parallel_requests(program, query, worker_count):
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        results = []
        for i in range(worker_count):
            for j in range(REQUESTS_PER_WORKER):
                results.append(executor.submit(run_api_program, program, query))
        return [r.result() for r in results]

# Test both programs with different worker counts
for worker_count in WORKER_COUNTS:
    print(f'Testing with {worker_count} worker(s)')

    print('Running API program without cache...')
    api_program = 'python3 api.py'
    results_without_cache = run_parallel_requests(api_program, QUERY, worker_count)
    times_without_cache = [t for r, t in results_without_cache]
    avg_time_without_cache = sum(times_without_cache) / len(times_without_cache)
    print(f'Average time taken without cache: {avg_time_without_cache:.2f} seconds')

    print('Running API program with cache...')
    api_cache_program = 'python3 apiCache.py'
    results_with_cache = run_parallel_requests(api_cache_program, QUERY, worker_count)
    times_with_cache = [t for r, t in results_with_cache]
    avg_time_with_cache = sum(times_with_cache) / len(times_with_cache)
    print(f'Average time taken with cache: {avg_time_with_cache:.2f} seconds')

    with open(RESULTS_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Worker Count', 'Method', 'Average Execution Time'])
        writer.writerow([worker_count, 'Without Cache', avg_time_without_cache])
        writer.writerow([worker_count, 'With Cache', avg_time_with_cache])

    print(f'Results written to {RESULTS_FILE} file')
