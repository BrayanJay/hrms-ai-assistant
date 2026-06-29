"use client"
                                
  import { useEffect, useState, useRef } from "react"
  import { Upload } from "lucide-react"
  import { Button } from "@/components/ui/button"
  import api from "@/lib/axios"
  import axios from "axios"

  interface Document {
      id: string
      filename: string
      file_type: string
      status: string
      created_at: string
  }

  const statusBadge = (status: string) => {
      const styles: Record<string, string> = {
          processing: "bg-yellow-500/10 text-yellow-400 border border-yellow-500/20",
          completed: "bg-green-500/10 text-green-400 border border-green-500/20",
          failed: "bg-red-500/10 text-red-400 border border-red-500/20",
      }
      return (
          <span className={`px-2 py-1 rounded-md text-xs font-medium ${styles[status] ?? styles.processing}`}>
              {status}
          </span>
      )
  }

  export default function DocumentsPage() {
      const [documents, setDocuments] = useState<Document[]>([])
      const [uploading, setUploading] = useState(false)
      const [error, setError] = useState("")
      const fileInputRef = useRef<HTMLInputElement>(null)

      const fetchDocuments = async () => {
          try {
              const res = await api.get("/documents/")
              setDocuments(res.data)
          } catch {
              setError("Failed to load documents.")
          }
      }

      useEffect(() => {
          fetchDocuments()
      }, [])

      const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
          const file = e.target.files?.[0]
          if (!file) return

          setUploading(true)
          setError("")

          const formData = new FormData()
          formData.append("file", file)

          try {
              await api.post("/documents/upload", formData, {
                  headers: { "Content-Type": "multipart/form-data" }
              })
              await fetchDocuments()
          } catch (err) {
              if (axios.isAxiosError(err)) {
                  setError(err.response?.data?.detail ?? "Upload failed.")
              }
          } finally {
              setUploading(false)
              if (fileInputRef.current) fileInputRef.current.value = ""
          }
      }

      return (
          <div className="space-y-6">
              <div className="flex items-center justify-between">
                  <div>
                      <h2 className="text-xl font-semibold text-white">Documents</h2>
                      <p className="text-sm text-zinc-400 mt-1">Manage your knowledge base documents</p>
                  </div>
                  <Button
                      onClick={() => fileInputRef.current?.click()}
                      disabled={uploading}
                      className="bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-2"
                  >
                      <Upload size={16} />
                      {uploading ? "Uploading..." : "Upload Document"}
                  </Button>
                  <input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf,.docx,.pptx,.xlsx"
                      onChange={handleUpload}
                      className="hidden"
                  />
              </div>

              {error && <p className="text-sm text-red-400">{error}</p>}

              <div className="rounded-lg border border-zinc-800 overflow-hidden">
                  <table className="w-full text-sm">
                      <thead className="bg-zinc-900 text-zinc-400">
                          <tr>
                              <th className="px-4 py-3 text-left font-medium">Filename</th>
                              <th className="px-4 py-3 text-left font-medium">Type</th>
                              <th className="px-4 py-3 text-left font-medium">Status</th>
                              <th className="px-4 py-3 text-left font-medium">Uploaded</th>
                          </tr>
                      </thead>
                      <tbody className="divide-y divide-zinc-800">
                          {documents.length === 0 ? (
                              <tr>
                                  <td colSpan={4} className="px-4 py-8 text-center text-zinc-500">
                                      No documents uploaded yet
                                  </td>
                              </tr>
                          ) : (
                              documents.map((doc) => (
                                  <tr key={doc.id} className="text-zinc-300 hover:bg-zinc-900/50">
                                      <td className="px-4 py-3">{doc.filename}</td>
                                      <td className="px-4 py-3 uppercase text-xs text-zinc-400">{doc.file_type}</td>
                                      <td className="px-4 py-3">{statusBadge(doc.status)}</td>
                                      <td className="px-4 py-3 text-zinc-400">
                                          {new Date(doc.created_at).toLocaleDateString()}
                                      </td>
                                  </tr>
                              ))
                          )}
                      </tbody>
                  </table>
              </div>
          </div>
      )
  }