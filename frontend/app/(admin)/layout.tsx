"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { FileText, LogOut, Database, BarChart2 } from "lucide-react"
import api from "@/lib/axios"
import { useEffect, useState } from "react"
import axios from "axios"

export default function AdminLayout({ children }: { children: React.ReactNode }) {
    const router = useRouter()
    const [isLoading, setIsLoading] = useState(true)
    const [isAuthorized, setIsAuthorized] = useState(false)

    const handleLogout = async () => {
        try {
            await api.post("/auth/logout")
        } finally {
            router.push("/auth/login")
        }
    }

    useEffect(() => {
        const check = async () => {
            try {
                await api.get("/auth/me")
                setIsLoading(false)
                setIsAuthorized(true)

            } catch (err) {
                if (axios.isAxiosError(err)) {
                    router.push(`/auth/login?error=${err.response?.data?.detail ?? "Authentication Failed"}`)
                } else {
                    router.push("/auth/login?error=An unexpected error occurred")
                }
            }
        }
        check()
    }, [])

    if (isLoading) return null
    if (!isAuthorized) return null

    return (
        <div className="min-h-screen flex bg-zinc-950">
            {/* Sidebar */}
            <aside className="w-64 flex flex-col border-r border-zinc-800 px-4 py-6">
                <div className="mb-8">
                    <h1 className="text-lg font-semibold text-white">
                        Astrynox <span className="text-blue-500">AI</span>
                    </h1>
                    <p className="text-xs text-zinc-500 mt-1">Admin Dashboard</p>
                </div>

                <nav className="flex-1 space-y-1">
                    <Link href="/documents" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors">
                        <FileText size={16} />
                        Documents
                    </Link>
                    <Link href="/qdrant" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors">
                        <Database size={16} />
                        Qdrant
                    </Link>
                    <Link href="/accuracy" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors">
                        <BarChart2 size={16} />
                        Accuracy
                    </Link>
                </nav>

                <button
                    onClick={handleLogout}
                    className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-zinc-400 hover:text-red-400 hover:bg-zinc-800 transition-colors">
                    <LogOut size={16} />
                    Logout
                </button>
            </aside>

            {/* Main content */}
            <main className="flex-1 p-8">
                {children}
            </main>
        </div>
    )
}