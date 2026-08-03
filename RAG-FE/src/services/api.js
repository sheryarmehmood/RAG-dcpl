import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const queryDocuments = (question) => api.post('/query/', { question })

export const ingestDocuments = () => api.post('/ingest/', {})

export const uploadDocument = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/documents/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

export const listDocuments = () => api.get('/documents/')

export const deleteDocument = (filename) => api.delete(`/documents/${encodeURIComponent(filename)}/`)

export const reindexDocument = (filename) => api.post(`/documents/${encodeURIComponent(filename)}/`, {})

export default api
