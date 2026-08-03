from django.urls import path

from . import views


urlpatterns = [
    path("ingest/", views.ingest, name="ingest"),
    path("documents/upload/", views.upload_document, name="upload_document"),
    path("documents/", views.documents, name="documents"),
    path("documents/<path:filename>/", views.document_detail, name="document_detail"),
    path("query/", views.query, name="query"),
    path("query/stream/", views.query_stream, name="query_stream"),
]