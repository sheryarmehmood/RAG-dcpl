from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Document


class DocumentStatusTests(TestCase):
	def test_document_status_transitions_are_persisted(self):
		document = Document.objects.create(
			filename="example.pdf",
			status=Document.Status.UPLOADED,
		)

		self.assertEqual(document.status, Document.Status.UPLOADED)
		document.status = Document.Status.INDEXING
		document.save()
		self.assertEqual(
			Document.objects.get(pk=document.pk).status,
			Document.Status.INDEXING,
		)

	def test_upload_validation_rejects_unsupported_file(self):
		response = self.client.post(
			reverse("upload_document"),
			{"file": SimpleUploadedFile("notes.exe", b"invalid")},
		)

		self.assertEqual(response.status_code, 400)
		self.assertEqual(Document.objects.count(), 0)
