<script setup>
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import { onMounted, ref } from 'vue'

import {
  deleteDocument,
  ingestDocuments,
  listDocuments,
  queryDocuments,
  reindexDocument,
  uploadDocument,
} from '../services/api'

const question = ref('')
const answer = ref('')
const sources = ref([])
const conversation = ref([])
const error = ref('')
const isAsking = ref(false)
const isIngesting = ref(false)
const isUploading = ref(false)
const ingestMessage = ref('')
const documents = ref([])
const documentAction = ref('')
const copied = ref(false)

const timestamp = () => new Intl.DateTimeFormat(undefined, {
  hour: 'numeric',
  minute: '2-digit',
}).format(new Date())

const askQuestion = async () => {
  const value = question.value.trim()
  if (!value || isAsking.value) return

  error.value = ''
  ingestMessage.value = ''
  isAsking.value = true
  conversation.value.push({ role: 'user', content: value, timestamp: timestamp() })

  try {
    const response = await queryDocuments(value)
    answer.value = response.data.answer
    sources.value = response.data.sources || []
    conversation.value.push({
      role: 'assistant',
      content: response.data.answer,
      sources: response.data.sources || [],
      noContext: response.data.no_context || false,
      timestamp: timestamp(),
    })
  } catch (requestError) {
    answer.value = ''
    sources.value = []
    conversation.value.push({
      role: 'assistant',
      content: requestError.response?.data?.error || 'The question could not be answered.',
      timestamp: timestamp(),
      isError: true,
    })
    error.value = requestError.response?.data?.error || 'The question could not be answered.'
  } finally {
    isAsking.value = false
  }
}

const ingest = async () => {
  if (isIngesting.value) return

  error.value = ''
  ingestMessage.value = ''
  isIngesting.value = true

  try {
    const response = await ingestDocuments()
    ingestMessage.value = `${response.data.chunks_added} new chunks indexed. ${response.data.chunks_after} total chunks available.`
    await loadDocuments()
  } catch (requestError) {
    error.value = requestError.response?.data?.error || 'Documents could not be indexed.'
  } finally {
    isIngesting.value = false
  }
}

const loadDocuments = async () => {
  try {
    const response = await listDocuments()
    documents.value = response.data.documents || []
  } catch (requestError) {
    error.value = requestError.response?.data?.error || 'Indexed documents could not be loaded.'
  }
}

const reindex = async (filename) => {
  if (documentAction.value) return

  error.value = ''
  ingestMessage.value = ''
  documentAction.value = `reindex:${filename}`
  try {
    const response = await reindexDocument(filename)
    ingestMessage.value = `${response.data.filename} re-indexed: ${response.data.chunks_stored} chunks stored.`
    await loadDocuments()
  } catch (requestError) {
    error.value = requestError.response?.data?.error || 'The document could not be re-indexed.'
  } finally {
    documentAction.value = ''
  }
}

const removeDocument = async (filename) => {
  if (documentAction.value || !window.confirm(`Delete ${filename}?`)) return

  error.value = ''
  ingestMessage.value = ''
  documentAction.value = `delete:${filename}`
  try {
    const response = await deleteDocument(filename)
    ingestMessage.value = `${response.data.filename} deleted.`
    await loadDocuments()
  } catch (requestError) {
    error.value = requestError.response?.data?.error || 'The document could not be deleted.'
  } finally {
    documentAction.value = ''
  }
}

const resetWorkspace = () => {
  question.value = ''
  answer.value = ''
  sources.value = []
  conversation.value = []
  error.value = ''
  ingestMessage.value = ''
  copied.value = false
}

const copyAnswer = async () => {
  if (!answer.value) return
  await navigator.clipboard.writeText(answer.value)
  copied.value = true
  window.setTimeout(() => { copied.value = false }, 1600)
}

const upload = async (event) => {
  const file = event.target.files?.[0]
  if (!file || isUploading.value) return

  error.value = ''
  ingestMessage.value = ''
  isUploading.value = true

  try {
    const response = await uploadDocument(file)
    ingestMessage.value = `${response.data.filename} indexed: ${response.data.chunks_stored} new chunks added.`
    await loadDocuments()
  } catch (requestError) {
    error.value = requestError.response?.data?.error || 'The document could not be uploaded.'
  } finally {
    isUploading.value = false
    event.target.value = ''
  }
}

onMounted(loadDocuments)
</script>

<template>
  <main class="workspace-shell">
    <header class="topbar">
      <div class="brand-lockup">
        <span class="brand-mark">R</span>
        <div>
          <p class="eyebrow">Local knowledge studio</p>
          <h1>Recall</h1>
        </div>
      </div>
      <div class="connection-status"><span></span> Ollama connected locally</div>
    </header>

    <footer class="workspace-footer">
      <span>INDEXED KNOWLEDGE</span>
      <div class="index-actions">
        <label class="upload-button" :class="{ disabled: isUploading }">
          {{ isUploading ? 'Uploading...' : 'Upload document' }} <span aria-hidden="true">&#8593;</span>
          <input
            type="file"
            accept=".pdf,.docx,.txt,.md,.markdown"
            :disabled="isUploading"
            @change="upload"
          />
        </label>
        <button class="ingest-button" type="button" :disabled="isIngesting" @click="ingest">
          {{ isIngesting ? 'Indexing...' : 'Refresh index' }} <span aria-hidden="true">&#8599;</span>
        </button>
      </div>
    </footer>

    <section class="query-panel" aria-labelledby="question-heading">
      <div class="panel-heading">
        <div>
          <span class="step-number">01</span>
        </div>
        <button class="text-button" type="button" @click="resetWorkspace">Clear</button>
      </div>
      <form @submit.prevent="askQuestion">
        <textarea
          v-model="question"
          aria-label="Question about your documents"
          placeholder="Ask anything"
          rows="1"
        ></textarea>
        <div class="form-actions">
          <span class="hint">Answers are grounded in your indexed documents.</span>
          <button class="primary-button" type="submit" :disabled="isAsking || !question.trim()">
            {{ isAsking ? 'Searching...' : 'ASK' }}
            <span aria-hidden="true">&#8599;</span>
          </button>
        </div>
      </form>
    </section>

    <p v-if="error" class="notice error-notice" role="alert">{{ error }}</p>
    <p v-if="ingestMessage" class="notice success-notice" role="status">{{ ingestMessage }}</p>

    <section v-if="conversation.length || isAsking" class="answer-panel" aria-live="polite">
      <div class="panel-heading">
        <div>
          <span class="step-number">02</span>
          <h3>Conversation</h3>
        </div>
        <button v-if="answer" class="text-button" type="button" @click="copyAnswer">
          {{ copied ? 'Copied' : 'Copy answer' }}
        </button>
      </div>
      <div v-for="message in conversation" :key="`${message.timestamp}-${message.content}`" class="message" :class="message.role">
        <div class="message-meta">
          <span>{{ message.role === 'user' ? 'You' : 'Recall' }}</span>
          <time>{{ message.timestamp }}</time>
        </div>
        <div v-if="message.role === 'assistant' && !message.isError" class="answer-copy markdown-copy" v-html="DOMPurify.sanitize(marked.parse(message.content))"></div>
        <p v-else class="answer-copy">{{ message.content }}</p>
        <p v-if="message.noContext" class="no-answer">No matching context was found in the indexed documents.</p>
        <div v-if="message.sources?.length" class="message-sources">
          <span v-for="source in message.sources" :key="`${source.citation}-${source.source}`">[{{ source.citation }}] {{ source.source }} · chunk {{ source.chunk_index }}</span>
        </div>
      </div>
      <div v-if="isAsking" class="loading-state"><span></span><span></span><span></span></div>
    </section>

    <section v-if="sources.length" class="sources-section">
      <div class="panel-heading">
        <div>
          <span class="step-number">03</span>
          <h3>Retrieved sources</h3>
        </div>
        <span class="source-count">{{ sources.length }} chunks</span>
      </div>
      <details v-for="source in sources" :key="`${source.source}-${source.chunk_index}`" class="source-item">
        <summary>
          <span>{{ source.source }}</span>
          <span>Chunk {{ source.chunk_index }} <b>&#8599;</b></span>
        </summary>
        <p>{{ source.content }}</p>
      </details>
    </section>

    <section v-if="documents.length" class="documents-section" aria-labelledby="documents-heading">
      <div class="panel-heading">
        <div>
          <span class="step-number">04</span>
          <h3 id="documents-heading">Indexed documents</h3>
        </div>
        <span class="source-count">{{ documents.length }} files</span>
      </div>
      <div v-for="document in documents" :key="document.filename" class="document-row">
        <div>
          <strong>{{ document.filename }}</strong>
          <span>{{ document.status }} · {{ document.chunks }} chunks indexed</span>
        </div>
        <div class="document-actions">
          <button
            class="text-button"
            type="button"
            :disabled="!!documentAction"
            @click="reindex(document.filename)"
          >
            {{ documentAction === `reindex:${document.filename}` ? 'Indexing...' : 'Re-index' }}
          </button>
          <button
            class="delete-button"
            type="button"
            :disabled="!!documentAction"
            @click="removeDocument(document.filename)"
          >
            {{ documentAction === `delete:${document.filename}` ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </section>
  </main>
</template>
