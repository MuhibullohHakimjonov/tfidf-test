import heapq
import math
import re
from collections import Counter, defaultdict

token_pattern = re.compile(r'\b\w+\b')


def tokenize(text):
	return token_pattern.findall(text.lower())


def compute_global_tfidf_table(documents):
	N = len(documents)
	df = defaultdict(int)
	tokenized_docs = []

	# Предварительная токенизация всех документов + расчет DF
	for doc in documents:
		tokens = tokenize(doc)
		tokenized_docs.append(tokens)
		unique_tokens = set(tokens)
		for word in unique_tokens:
			df[word] += 1

	# IDF для всех слов
	global_idf = {word: math.log(N / count) for word, count in df.items()}

	# Топ-50 слов по IDF
	top_words = heapq.nlargest(50, global_idf.items(), key=lambda x: x[1])
	top_word_list = [word for word, _ in top_words]

	results = []
	word_counts = []

	# Расчет TF для топ-50 слов по каждому документу
	for tokens in tokenized_docs:
		total_words = len(tokens)
		word_counts.append(total_words)

		tf_counter = Counter(tokens)
		doc_result = [
			{
				"word": word,
				"tf": round(tf_counter[word] / total_words, 6) if total_words else 0,
				"idf": round(global_idf[word], 6)
			}
			for word in top_word_list
		]
		results.append(doc_result)

	return results, word_counts


class HuffmanNode:
	def __init__(self, char, freq):
		self.char = char
		self.freq = freq
		self.left = None
		self.right = None

	def __lt__(self, other):
		return self.freq < other.freq


def build_huffman_tree(text):
	freq_counter = Counter(text)
	heap = [HuffmanNode(char, freq) for char, freq in freq_counter.items()]
	heapq.heapify(heap)

	while len(heap) > 1:
		node1 = heapq.heappop(heap)
		node2 = heapq.heappop(heap)
		merged = HuffmanNode(None, node1.freq + node2.freq)
		merged.left = node1
		merged.right = node2
		heapq.heappush(heap, merged)

	return heap[0] if heap else None


def generate_codes(node, prefix="", code_map=None):
	if code_map is None:
		code_map = {}

	if node is not None:
		if node.char is not None:
			code_map[node.char] = prefix
		generate_codes(node.left, prefix + "0", code_map)
		generate_codes(node.right, prefix + "1", code_map)

	return code_map


def huffman_encode(text, code_map):
	return ''.join(code_map[char] for char in text)
