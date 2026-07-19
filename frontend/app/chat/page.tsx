"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import api from "@/lib/axios"
import axios from "axios"

type Citation = {
    citation: number
    type: string
    content?: string
    image_bytes?: string
    doc_id?: string
}

type Message = {
    role: "user" | "assistant"
    content: string
    citations?: Citation[]
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([])
    const [query, setQuery] = useState("")
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState("")
    const [sessionId, setSessionId] = useState<string | null>(null)
    const [expandedCitations, setExpandedCitations] = useState<Set<number>>(new Set())
    const bottomRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        createSession()
    }, [])

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages])

    const createSession = async () => {
        try {
            const res = await api.post("/chat_session/")
            setSessionId(res.data.session_id)
            setMessages([])
        } catch {
            setError("Failed to start session. Please refresh.")
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!query.trim() || !sessionId) return

        const userMessage: Message = { role: "user", content: query }
        setMessages(prev => [...prev, userMessage])
        setQuery("")
        setLoading(true)
        setError("")

        try {
            const res = await api.post("/query/", { query: userMessage.content, session_id: sessionId })
            const assistantMessage: Message = {
                role: "assistant",
                content: res.data.answer,
                citations: res.data.citations
            }
            setMessages(prev => [...prev, assistantMessage])
        } catch (err) {
            if (axios.isAxiosError(err)) {
                setError(err.response?.data?.detail ?? "Something went wrong.")
            } else {
                setError("An unexpected error occurred.")
            }
        } finally {
            setLoading(false)
        }
    }

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            handleSubmit(e as unknown as React.FormEvent)
        }
    }

    const toggleCitations = (index: number) => {
        setExpandedCitations(prev => {
            const next = new Set(prev)
            next.has(index) ? next.delete(index) : next.add(index)
            return next
        })
    }

    return (
        <div className="flex flex-col h-screen bg-zinc-950 text-white">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800">
                <div>
                    <h1 className="text-lg font-semibold">Astrynox <span className="text-blue-500">AI</span></h1>
                    <p className="text-xs text-zinc-500">HR & Compliance Assistant</p>
                </div>
                <Button
                    onClick={createSession}
                    variant="ghost"
                    className="text-zinc-400 hover:text-white hover:bg-zinc-800 text-sm"
                >
                    + New Chat
                </Button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-center space-y-3">
                        <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center text-xl font-bold">A</div>
                        <h2 className="text-xl font-semibold">Astrynox AI Assistant</h2>
                        <p className="text-zinc-400 text-sm max-w-md">
                            Your internal HR & Compliance knowledge assistant. Ask me anything about policies, procedures, or employee information.
                        </p>
                    </div>
                )}

                {messages.map((msg, index) => (
                    <div key={index} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                        <div className={`max-w-[75%] space-y-2`}>
                            <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                                msg.role === "user"
                                    ? "bg-blue-600 text-white rounded-br-sm"
                                    : "bg-zinc-800 text-zinc-100 rounded-bl-sm"
                            }`}>
                                {msg.content}
                            </div>

                            {msg.role === "assistant" && msg.citations && msg.citations.length > 0 && (
                                <div className="pl-1">
                                    <button
                                        onClick={() => toggleCitations(index)}
                                        className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
                                    >
                                        {expandedCitations.has(index) ? "Hide" : "Show"} {msg.citations.length} source{msg.citations.length > 1 ? "s" : ""}
                                    </button>

                                    {expandedCitations.has(index) && (
                                        <div className="mt-2 space-y-2">
                                            {msg.citations.map((c) => (
                                                <div key={c.citation} className="bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-xs text-zinc-400">
                                                    <span className="text-blue-400 font-medium">[{c.citation}]</span>{" "}
                                                    {c.type === "image" ? (
                                                        <span className="text-zinc-500 italic">Image source</span>
                                                    ) : (
                                                        <span>{c.content}</span>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-zinc-800 rounded-2xl rounded-bl-sm px-4 py-3 text-sm text-zinc-400">
                            <span className="animate-pulse">Thinking...</span>
                        </div>
                    </div>
                )}

                <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div className="border-t border-zinc-800 px-4 py-4">
                {error && <p className="text-xs text-red-400 mb-2">{error}</p>}
                <form onSubmit={handleSubmit} className="flex gap-3 items-end">
                    <Textarea
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask about HR policies, employee info, compliance..."
                        rows={1}
                        className="flex-1 resize-none bg-zinc-900 border-zinc-700 text-white placeholder:text-zinc-600 focus-visible:ring-blue-500 rounded-xl"
                    />
                    <Button
                        type="submit"
                        disabled={loading || !query.trim()}
                        className="bg-blue-600 hover:bg-blue-500 text-white px-5 rounded-xl"
                    >
                        Send
                    </Button>
                </form>
                <p className="text-xs text-zinc-600 mt-2 text-center">Press Enter to send · Shift+Enter for new line</p>
            </div>
        </div>
    )
}
