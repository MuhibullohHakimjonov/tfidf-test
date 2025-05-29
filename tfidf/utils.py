import math
from collections import Counter


def tokenize(text):
	# Простая токенизация: разбиваем по пробелам и чистим от знаков препинания
	import re
	words = re.findall(r'\b\w+\b', text.lower())
	return words


def compute_tfidf_for_documents(documents):
	N = len(documents)
	df = {}

	# Подсчёт document frequency
	for doc in documents:
		unique_words = set(tokenize(doc))
		for w in unique_words:
			df[w] = df.get(w, 0) + 1

	results = []
	word_counts = []

	for doc in documents:
		words = tokenize(doc)
		tf_counter = Counter(words)
		total_words = len(words) or 1
		word_counts.append(total_words)

		doc_result = []
		for word, count in tf_counter.items():
			tf = count / total_words
			idf = math.log((N) / (1 + df[word])) + 1
			doc_result.append({
				"word": word,
				"tf": round(tf, 6),
				"idf": round(idf, 6),
			})

		doc_result.sort(key=lambda x: x["idf"], reverse=True)
		results.append(doc_result[:50])

	return results, word_counts
