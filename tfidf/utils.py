import math
import re
from collections import Counter


def tokenize(text):
	"""
	Splits text into alphanumeric words in lower case.
	"""
	return re.findall(r'\b\w+\b', text.lower())


def compute_global_tfidf_table(documents):
	"""
	Compute a global TF-IDF table for a list of document texts.

	Steps:
	  1. Compute document frequency (DF) for each word across all documents.
	  2. Calculate the global inverse document frequency (IDF) for each word.
	  3. Sort and pick the top 50 words by highest global IDF.
	  4. For each document, compute its TF (term frequency) for each of these words.

	Returns:
	  - A list (one per document) with dictionaries containing "word", "tf", and "idf".
	  - A matching list of total word counts for each document.
	"""
	N = len(documents)
	df = {}

	# Step 1: Calculate document frequency (df) over all documents
	for doc in documents:
		unique_words = set(tokenize(doc))
		for word in unique_words:
			df[word] = df.get(word, 0) + 1

	# Step 2: Compute global IDF for each word
	global_idf = {}
	for word, count in df.items():
		# Avoid division by zero even if count is 0; although by design count > 0.
		global_idf[word] = math.log(N / count) if count > 0 else 0

	# Step 3: Sort words by global IDF in descending order and obtain the top 50
	top_50_words = sorted(global_idf.items(), key=lambda x: x[1], reverse=True)[:50]
	# Extract just the word list in order
	top_50_words = [word for word, _ in top_50_words]

	# Step 4: For each document, compute TF for each top word.
	results = []
	word_counts = []
	for doc in documents:
		words = tokenize(doc)
		total_words = len(words) or 1  # safeguard against division by zero
		word_counts.append(total_words)
		tf_counter = Counter(words)

		doc_result = []
		for word in top_50_words:
			tf = tf_counter.get(word, 0) / total_words
			doc_result.append({
				"word": word,
				"tf": round(tf, 6),
				"idf": round(global_idf[word], 6)
			})
		results.append(doc_result)

	return results, word_counts
