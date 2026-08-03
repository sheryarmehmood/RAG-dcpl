import json
from pathlib import Path

from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Document
from rag.ingest import ingest_documents
from rag.query import build_context, build_prompt, search_documents
from rag.llm import generate_answer, generate_answer_stream
from rag.config import SIMILARITY_THRESHOLD, TOP_K_RESULTS
from rag.vectordb import VectorDatabase
from rag.config import DATA_DIR
from rag.ingest import SUPPORTED_EXTENSIONS


@csrf_exempt
def ingest(request):
	if request.method != "POST":
		return JsonResponse(
			{"error": "Only POST requests are allowed."},
			status=405,
		)

	try:
		database = VectorDatabase()
		before = database.count()
		ingest_documents()
		after = database.count()
	except Exception as error:
		return JsonResponse(
			{"error": str(error)},
			status=500,
		)

	return JsonResponse(
		{
			"message": "Ingestion completed.",
			"chunks_before": before,
			"chunks_after": after,
			"chunks_added": after - before,
		}
	)


@csrf_exempt
def upload_document(request):
	if request.method != "POST":
		return JsonResponse(
			{"error": "Only POST requests are allowed."},
			status=405,
		)

	upload = request.FILES.get("file")
	if upload is None:
		return JsonResponse(
			{"error": "A file field is required."},
			status=400,
		)

	filename = Path(upload.name).name
	suffix = Path(filename).suffix.lower()
	if suffix not in SUPPORTED_EXTENSIONS:
		return JsonResponse(
			{"error": "Supported file types are PDF, DOCX, TXT, and Markdown."},
			status=400,
		)

	if not filename:
		return JsonResponse(
			{"error": "The uploaded file must have a name."},
			status=400,
		)

	target = DATA_DIR / filename
	with target.open("wb") as destination:
		for chunk in upload.chunks():
			destination.write(chunk)

	document, _ = Document.objects.update_or_create(
		filename=filename,
		defaults={"status": Document.Status.UPLOADED, "error_message": ""},
	)
	document.status = Document.Status.INDEXING
	document.save(update_fields=["status", "updated_at"])

	try:
		before = VectorDatabase().count()
		stats = ingest_documents([target])
		stats["chunks_before"] = before
	except Exception as error:
		document.status = Document.Status.FAILED
		document.error_message = str(error)
		document.save(update_fields=["status", "error_message", "updated_at"])
		return JsonResponse(
			{"error": str(error)},
			status=500,
		)

	document.status = Document.Status.INDEXED
	document.chunk_count = stats["chunks_stored"] + stats["chunks_skipped"]
	document.error_message = ""
	document.save(update_fields=["status", "chunk_count", "error_message", "updated_at"])

	return JsonResponse(
		{
			"message": "Document uploaded and indexed.",
			"filename": filename,
			**stats,
		}
	)


def documents(request):
	if request.method != "GET":
		return JsonResponse(
			{"error": "Only GET requests are allowed."},
			status=405,
		)

	database = VectorDatabase()
	indexed_sources = database.get_source_documents()
	indexed_names = {item["source"] for item in indexed_sources}

	for source in indexed_sources:
		Document.objects.update_or_create(
			filename=source["source"],
			defaults={"status": Document.Status.INDEXED, "chunk_count": source["chunks"]},
		)

	return JsonResponse({
		"documents": [
			{
				"filename": document.filename,
				"status": document.status,
				"chunks": document.chunk_count,
				"error": document.error_message,
			}
			for document in Document.objects.order_by("filename")
			if document.filename in indexed_names or document.status != Document.Status.INDEXED
		]
	})


@csrf_exempt
def document_detail(request, filename):
	source = Path(filename).name
	if source != filename:
		return JsonResponse({"error": "Invalid document name."}, status=400)

	database = VectorDatabase()
	known_sources = {
		document["source"]
		for document in database.get_source_documents()
	}
	if source not in known_sources:
		return JsonResponse({"error": "Document not found."}, status=404)

	if request.method == "DELETE":
		deleted_chunks = database.delete_source(source)
		file_path = DATA_DIR / source
		if file_path.exists():
			file_path.unlink()
		Document.objects.filter(filename=source).delete()
		return JsonResponse(
			{
				"message": "Document deleted.",
				"filename": source,
				"chunks_deleted": deleted_chunks,
			}
		)

	if request.method == "POST":
		file_path = DATA_DIR / source
		if not file_path.exists():
			return JsonResponse(
			{"error": "The source file is not available for re-indexing."},
			status=404,
		)

		deleted_chunks = database.delete_source(source)
		document, _ = Document.objects.get_or_create(filename=source)
		document.status = Document.Status.INDEXING
		document.error_message = ""
		document.save(update_fields=["status", "error_message", "updated_at"])
		try:
			stats = ingest_documents([file_path])
		except Exception as error:
			document.status = Document.Status.FAILED
			document.error_message = str(error)
			document.save(update_fields=["status", "error_message", "updated_at"])
			return JsonResponse({"error": str(error)}, status=500)
		document.status = Document.Status.INDEXED
		document.chunk_count = stats["chunks_stored"] + stats["chunks_skipped"]
		document.save(update_fields=["status", "chunk_count", "updated_at"])
		return JsonResponse(
			{
				"message": "Document re-indexed.",
				"filename": source,
				"chunks_deleted": deleted_chunks,
				**stats,
			}
		)

	return JsonResponse(
		{"error": "Only POST and DELETE requests are allowed."},
		status=405,
	)


@csrf_exempt
def query(request):
	if request.method != "POST":
		return JsonResponse(
			{"error": "Only POST requests are allowed."},
			status=405,
		)

	try:
		payload = json.loads(request.body or "{}")
	except json.JSONDecodeError:
		return JsonResponse(
			{"error": "Request body must be valid JSON."},
			status=400,
		)

	question = str(payload.get("question", "")).strip()
	if not question:
		return JsonResponse(
			{"error": "The question field is required."},
			status=400,
		)

	try:
		top_k = max(1, int(payload.get("top_k", TOP_K_RESULTS)))
		similarity_threshold = payload.get(
			"similarity_threshold",
			SIMILARITY_THRESHOLD,
		)
		similarity_threshold = float(similarity_threshold)
		results = search_documents(
			question,
			top_k=top_k,
			similarity_threshold=similarity_threshold,
		)
		if not results.get("documents", [[]])[0]:
			return JsonResponse(
				{
					"question": question,
					"answer": "I could not find the answer in the provided documents.",
					"sources": [],
					"no_context": True,
				}
			)
		context = build_context(results)
		answer = generate_answer(
			build_prompt(context=context, question=question)
		).strip()
	except Exception as error:
		return JsonResponse(
			{"error": str(error)},
			status=500,
		)

	documents = results["documents"][0]
	metadatas = results["metadatas"][0]
	distances = results["distances"][0]

	sources = [
		{
			"citation": index,
			"source": metadata.get("source", "Unknown source"),
			"chunk_index": metadata.get("chunk_index"),
			"distance": distance,
			"content": document,
		}
		for index, (document, metadata, distance) in enumerate(zip(
			documents,
			metadatas,
			distances,
		), start=1)
	]

	return JsonResponse(
		{
			"question": question,
			"answer": answer,
			"sources": sources,
			"no_context": False,
		}
	)


@csrf_exempt
def query_stream(request):
	if request.method != "POST":
		return JsonResponse({"error": "Only POST requests are allowed."}, status=405)

	try:
		payload = json.loads(request.body or "{}")
		question = str(payload.get("question", "")).strip()
		if not question:
			return JsonResponse({"error": "The question field is required."}, status=400)
		top_k = max(1, int(payload.get("top_k", TOP_K_RESULTS)))
		threshold = float(payload.get("similarity_threshold", SIMILARITY_THRESHOLD))
		results = search_documents(question, top_k=top_k, similarity_threshold=threshold)
		if not results.get("documents", [[]])[0]:
			return StreamingHttpResponse(
				["I could not find the answer in the provided documents."],
				content_type="text/plain; charset=utf-8",
			)
		prompt = build_prompt(build_context(results), question)
	except (ValueError, json.JSONDecodeError) as error:
		return JsonResponse({"error": str(error)}, status=400)
	except Exception as error:
		return JsonResponse({"error": str(error)}, status=500)

	return StreamingHttpResponse(
		generate_answer_stream(prompt),
		content_type="text/plain; charset=utf-8",
	)
