from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import re
from collections import Counter, defaultdict
import math
import os
from .models import Document, WordOccurrence


def upload_file(request):
	error_message = None

	if request.method == 'POST':
		text_files = request.FILES.getlist('text_files')
		if not text_files:
			error_message = "Please select at least one file to upload."
			return render(request, 'upload.html', {'error_message': error_message})

		try:
			fs = FileSystemStorage()
			all_word_counts = Counter()
			document_word_sets = defaultdict(set)
			total_documents = 0

			for text_file in text_files:
				filename = fs.save(text_file.name, text_file)
				file_path = fs.path(filename)

				document = Document.objects.create(file=filename)
				total_documents += 1

				try:
					with open(file_path, 'r', encoding='utf-8') as f:
						text = f.read()

					text = text.lower()
					words = re.findall(r'\b\w+\b', text)
					if not words:
						error_message = f"No valid words found in file '{text_file.name}'."
						raise ValueError(error_message)

					word_counts = Counter(words)
					all_word_counts.update(word_counts)
					document_word_sets[document.id] = set(word_counts.keys())

					for word, count in word_counts.items():
						WordOccurrence.objects.create(word=word, document=document, count=count)

				except Exception as e:
					document.delete()
					os.remove(file_path)
					return render(request, 'upload.html', {'error_message': str(e)})
				finally:
					if os.path.exists(file_path):
						os.remove(file_path)

			total_words = sum(all_word_counts.values())
			tf_scores = {
				word: round(count / total_words, 4)
				for word, count in all_word_counts.items()
			}
			df_counts = Counter()
			for doc_words in document_word_sets.values():
				for word in doc_words:
					df_counts[word] += 1
			idf_scores = {
				word: round(math.log(total_documents / df_counts[word]), 4)
				for word in df_counts
			}
			results = [
				{
					'word': word,
					'tf': tf_scores.get(word, 0),
					'count': all_word_counts[word],
					'idf': idf_scores.get(word, 0)
				}
				for word in all_word_counts.keys()
			]
			results = sorted(results, key=lambda x: x['idf'], reverse=True)[:50]

			return render(request, 'results.html', {'results': results})

		except Exception as e:
			error_message = f"Error processing files: {str(e)}"
			return render(request, 'upload.html', {'error_message': error_message})

	return render(request, 'upload.html', {'error_message': error_message})
