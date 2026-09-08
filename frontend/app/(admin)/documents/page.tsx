"use client"

import { useEffect, useState, useRef } from "react"
import { Upload, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import api from "@/lib/axios"
import axios from "axios"

interface Document {
    id: string
    filename: string
    file_type: string
    status: string
    doc_category: string
    created_at: string
}

const CATEGORIES = [
    { value: "policy", label: "Policy" },
    { value: "company-information", label: "Company Information" },
    { value: "navigation", label: "Navigation" },
]

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

const categoryBadge = (category: string) => {
    const styles: Record<string, string> = {
        "policy": "bg-blue-500/10 text-blue-400 border border-blue-500/20",
        "company-information": "bg-purple-500/10 text-purple-400 border border-purple-500/20",
        "navigation": "bg-zinc-500/10 text-zinc-400 border border-zinc-500/20",
    }
    const labels: Record<string, string> = {
        "policy": "Policy",
        "company-information": "Company Info",
        "navigation": "Navigation",
    }
    return (
        <span className={`px-2 py-1 rounded-md text-xs font-medium ${styles[category] ?? styles.policy}`}>
            {labels[category] ?? category}
        </span>
    )
}

export default function DocumentsPage() {
    const [documents, setDocuments] = useState<Document[]>([])
    const [uploading, setUploading] = useState(false)
    const [deletingId, setDeletingId] = useState<string | null>(null)
    const [error, setError] = useState("")
    const [category, setCategory] = useState("policy")
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
        formData.append("category", category)

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

    const handleDelete = async (doc: Document) => {
        if (!window.confirm(`Delete "${doc.filename}" and all its chunks? This cannot be undone.`)) return
        setDeletingId(doc.id)
        setError("")
        try {
            await api.delete(`/documents/${doc.id}`)
            setDocuments(prev => prev.filter(d => d.id !== doc.id))
        } catch (err) {
            if (axios.isAxiosError(err)) {
                setError(err.response?.data?.detail ?? "Delete failed.")
            }
        } finally {
            setDeletingId(null)
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-xl font-semibold text-white">Documents</h2>
                    <p className="text-sm text-zinc-400 mt-1">Manage your knowledge base documents</p>
                </div>
                <div className="flex items-center gap-3">
                    <select
                        value={category}
                        onChange={e => setCategory(e.target.value)}
                        className="bg-zinc-900 border border-zinc-700 text-zinc-300 text-sm rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    >
                        {CATEGORIES.map(c => (
                            <option key={c.value} value={c.value}>{c.label}</option>
                        ))}
                    </select>
                    <Button
                        onClick={() => fileInputRef.current?.click()}
                        disabled={uploading}
                        className="bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-2"
                    >
                        <Upload size={16} />
                        {uploading ? "Uploading..." : "Upload Document"}
                    </Button>
                </div>
                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.docx,.pptx"
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
                            <th className="px-4 py-3 text-left font-medium">Category</th>
                            <th className="px-4 py-3 text-left font-medium">Status</th>
                            <th className="px-4 py-3 text-left font-medium">Uploaded</th>
                            <th className="px-4 py-3" />
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-800">
                        {documents.length === 0 ? (
                            <tr>
                                <td colSpan={6} className="px-4 py-8 text-center text-zinc-500">
                                    No documents uploaded yet
                                </td>
                            </tr>
                        ) : (
                            documents.map((doc) => (
                                <tr key={doc.id} className="text-zinc-300 hover:bg-zinc-900/50 group">
                                    <td className="px-4 py-3">{doc.filename}</td>
                                    <td className="px-4 py-3 uppercase text-xs text-zinc-400">{doc.file_type}</td>
                                    <td className="px-4 py-3">{categoryBadge(doc.doc_category)}</td>
                                    <td className="px-4 py-3">{statusBadge(doc.status)}</td>
                                    <td className="px-4 py-3 text-zinc-400">
                                        {new Date(doc.created_at).toLocaleDateString()}
                                    </td>
                                    <td className="px-4 py-3 text-right">
                                        <button
                                            onClick={() => handleDelete(doc)}
                                            disabled={deletingId === doc.id}
                                            className="opacity-0 group-hover:opacity-100 text-zinc-600 hover:text-red-400 transition-all disabled:opacity-40"
                                        >
                                            <Trash2 size={15} />
                                        </button>
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
