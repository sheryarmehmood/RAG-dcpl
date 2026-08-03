from django.db import models


class Document(models.Model):
	class Status(models.TextChoices):
		UPLOADED = "uploaded", "Uploaded"
		INDEXING = "indexing", "Indexing"
		INDEXED = "indexed", "Indexed"
		FAILED = "failed", "Failed"

	filename = models.CharField(max_length=255, unique=True)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPLOADED)
	chunk_count = models.PositiveIntegerField(default=0)
	error_message = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.filename
