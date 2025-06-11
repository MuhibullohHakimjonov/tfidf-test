import math
import re
from collections import Counter
token_pattern = re.compile(r'\b\w+\b')


def tokenize(text):
	"""Tokenizes text by extracting alphanumeric words in lowercase."""
	return token_pattern.findall(text.lower())


def compute_global_tfidf_table(documents):
	"""
	Given a list of document texts, computes the TF-IDF table for the top
	50 words (by global idf score) across documents.

	Returns:
		results: A list (one per document) of dictionaries with keys 'word', 'tf', and 'idf'
		word_counts: A list of document word counts.
	"""
	N = len(documents)
	tokenized_docs = [tokenize(doc) for doc in documents]

	# Compute document frequency (df) by iterating each document's unique tokens
	df = Counter()
	for tokens in tokenized_docs:
		df.update(set(tokens))

	global_idf = {word: math.log(N / df[word]) for word in df}

	# Sort by idf descending and take top 50 words
	top_50_words = sorted(global_idf.items(), key=lambda x: x[1], reverse=True)[:50]
	top_words_set = set(word for word, _ in top_50_words)

	results = []
	word_counts = []

	for tokens in tokenized_docs:
		total_words = len(tokens)
		word_counts.append(total_words)
		tf_counter = Counter(tokens)
		doc_result = []

		for word in top_words_set:
			# Avoid division by zero
			tf = (tf_counter[word] / total_words) if total_words > 0 else 0
			doc_result.append({
				"word": word,
				"tf": round(tf, 6),
				"idf": round(global_idf[word], 6)
			})
		results.append(doc_result)
	return results, word_counts
