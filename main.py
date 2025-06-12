import requests
from concurrent.futures import ThreadPoolExecutor
import time

URLS = [
	'http://localhost:8000/api/documents/74/huffman/',
	'http://localhost:8000/api/documents/74/'
]
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ5ODA1NjE0LCJpYXQiOjE3NDk3MTkyMTQsImp0aSI6ImMyNjFmMzkxOGI5MjQ1NWRhZjMxOWQ2MjMzM2UxNzIzIiwidXNlcl9pZCI6Mn0.xrXj7JXZnbz5T0gj18n7cJHiQ87ce1QldcshLSFZ5QQ'

HEADERS = {
	'Authorization': f'Bearer {TOKEN}'
}


def make_request(url, n):
	try:
		response = requests.get(url, headers=HEADERS)
		print(f'Request {n} to {url}: Status {response.status_code}')
	except Exception as e:
		print(f'Request {n} to {url} failed: {e}')


def main():
	NUM_REQUESTS_PER_URL = 100
	MAX_WORKERS = 20  # total threads to handle both endpoints

	start_time = time.time()

	with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
		futures = []
		for url in URLS:
			for i in range(NUM_REQUESTS_PER_URL):
				futures.append(executor.submit(make_request, url, i + 1))

		for future in futures:
			future.result()

	end_time = time.time()
	print(f"\nCompleted {len(URLS) * NUM_REQUESTS_PER_URL} requests in {end_time - start_time:.2f} seconds")


if __name__ == '__main__':
	main()
