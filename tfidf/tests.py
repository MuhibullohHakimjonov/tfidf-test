from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .models import Document, WordOccurrence
import math


class TfidfAppTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.url = reverse('upload_file')

	def upload_file_and_get_results(self, files):
		response = self.client.post(self.url, {'text_files': files}, follow=True)
		self.assertEqual(response.status_code, 200)
		return response

	def test_upload_single_text_file(self):
		content = b"This is a test file with some words. Test words appear here."
		file = SimpleUploadedFile("test.txt", content, content_type="text/plain")

		response = self.upload_file_and_get_results([file])
		self.assertTemplateUsed(response, 'results.html')

		self.assertEqual(Document.objects.count(), 1)
		self.assertGreater(WordOccurrence.objects.count(), 0)
		for word in ['test', 'words']:
			self.assertTrue(WordOccurrence.objects.filter(word=word).exists())
		results = response.context['results']
		self.assertGreater(len(results), 0)
		self.assertLessEqual(len(results), 50)
		for item in results:
			self.assertIn('word', item)
			self.assertIn('tf', item)
			self.assertIn('count', item)
			self.assertIn('idf', item)

	def test_upload_multiple_text_files(self):
		file1 = SimpleUploadedFile("doc1.txt", b"First document with some unique words.", content_type="text/plain")
		file2 = SimpleUploadedFile("doc2.txt", b"Second document with some shared words.", content_type="text/plain")

		response = self.upload_file_and_get_results([file1, file2])
		self.assertTemplateUsed(response, 'results.html')
		self.assertEqual(Document.objects.count(), 2)
		self.assertGreater(WordOccurrence.objects.count(), 0)
		self.assertTrue(WordOccurrence.objects.filter(word='words').exists())
		self.assertTrue(WordOccurrence.objects.filter(word='unique').exists())
		total_docs = Document.objects.count()
		docs_with_words = WordOccurrence.objects.filter(word='words').values('document').distinct().count()
		expected_idf = round(math.log(total_docs / docs_with_words), 4)

		results = response.context['results']
		word_result = next((item for item in results if item['word'] == 'words'), None)
		self.assertIsNotNone(word_result)
		self.assertAlmostEqual(word_result['idf'], expected_idf)

	def test_upload_non_text_file(self):
		file = SimpleUploadedFile("binary.bin", b"\x00\x01\x02\x03", content_type="application/octet-stream")

		response = self.upload_file_and_get_results([file])
		self.assertTemplateUsed(response, 'upload.html')
		self.assertEqual(Document.objects.count(), 0)
		self.assertEqual(WordOccurrence.objects.count(), 0)

	def test_tf_calculation(self):
		file = SimpleUploadedFile("test_tf.txt", b"word1 word1 word2", content_type="text/plain")

		response = self.upload_file_and_get_results([file])
		results = response.context['results']

		word1 = next((item for item in results if item['word'] == 'word1'), None)
		word2 = next((item for item in results if item['word'] == 'word2'), None)

		self.assertIsNotNone(word1)
		self.assertIsNotNone(word2)
		self.assertEqual(word1['count'], 2)
		self.assertAlmostEqual(word1['tf'], round(2 / 3, 4))
		self.assertEqual(word2['count'], 1)
		self.assertAlmostEqual(word2['tf'], round(1 / 3, 4))

	def test_no_files_uploaded(self):
		response = self.client.post(self.url, {}, follow=True)
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'upload.html')
		self.assertContains(response, "Please select at least one file to upload")
