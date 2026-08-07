"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import api from "@/lib/axios"
import axios from "axios"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

type Citation = {
    citation: number
    type: string
    content?: string
    image_bytes?: string
    doc_id?: string
}

type ConfirmationPayload = {
    tool_name: string
    tool_params: Record<string, unknown>
    query: string
}

type Message = {
    role: "user" | "assistant"
    content: string
    citations?: Citation[]
    requiresConfirmation?: boolean
    pendingActionId?: string
    confirmationPayload?: ConfirmationPayload
    confirmationDone?: boolean
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

    const submitQuery = async (text: string) => {
        if (!text.trim() || !sessionId || loading) return

        const userMessage: Message = { role: "user", content: text }
        setMessages(prev => [...prev, userMessage])
        setQuery("")
        setLoading(true)
        setError("")

        try {
            const res = await api.post("/query/", { query: text, session_id: sessionId })

            if (res.data.requires_confirmation) {
                const confirmMessage: Message = {
                    role: "assistant",
                    content: res.data.answer,
                    requiresConfirmation: true,
                    pendingActionId: res.data.pending_action_id,
                    confirmationPayload: res.data.confirmation_payload,
                    confirmationDone: false,
                }
                setMessages(prev => [...prev, confirmMessage])
            } else {
                const assistantMessage: Message = {
                    role: "assistant",
                    content: res.data.answer,
                    citations: res.data.citations,
                }
                setMessages(prev => [...prev, assistantMessage])
            }
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

    const handleConfirm = async (actionId: string, confirmed: boolean) => {
        setMessages(prev =>
            prev.map(m => m.pendingActionId === actionId ? { ...m, confirmationDone: true } : m)
        )
        setLoading(true)
        setError("")

        try {
            const res = await api.post("/query/confirm", {
                session_id: sessionId,
                action_id: actionId,
                confirmed,
            })
            setMessages(prev => [...prev, {
                role: "assistant",
                content: res.data.answer,
                citations: res.data.citations,
            }])
        } catch (err) {
            if (axios.isAxiosError(err)) {
                setError(err.response?.data?.detail ?? "Confirmation failed.")
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
            submitQuery(query)
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
                        <div className="max-w-[75%] space-y-2">
                            <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                                msg.role === "user"
                                    ? "bg-blue-600 text-white rounded-br-sm"
                                    : "bg-zinc-800 text-zinc-100 rounded-bl-sm"
                            }`}>
                                {msg.role === "assistant" ? (
                                    <ReactMarkdown
                                        remarkPlugins={[remarkGfm]}
                                        components={{
                                            p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                                            ul: ({ children }) => <ul className="list-disc list-inside space-y-1 mb-2">{children}</ul>,
                                            ol: ({ children }) => <ol className="list-decimal list-inside space-y-1 mb-2">{children}</ol>,
                                            li: ({ children }) => <li className="text-zinc-100">{children}</li>,
                                            strong: ({ children }) => <strong className="text-white font-semibold">{children}</strong>,
                                            code: ({ children }) => <code className="bg-zinc-700 px-1 rounded text-xs">{children}</code>,
                                            table: ({ children }) => (
                                                <div className="overflow-x-auto my-2">
                                                    <table className="text-xs border-collapse w-full">{children}</table>
                                                </div>
                                            ),
                                            thead: ({ children }) => <thead className="border-b border-zinc-600">{children}</thead>,
                                            th: ({ children }) => <th className="px-3 py-2 text-left text-zinc-300 font-semibold whitespace-nowrap">{children}</th>,
                                            td: ({ children }) => <td className="px-3 py-2 text-zinc-200 border-t border-zinc-700">{children}</td>,
                                        }}
                                    >
                                        {msg.content}
                                    </ReactMarkdown>
                                ) : (
                                    msg.content
                                )}
                            </div>

                            {/* Maker-checker confirmation card */}
                            {msg.requiresConfirmation && (
                                <div className={`border rounded-xl p-4 space-y-3 transition-opacity ${
                                    msg.confirmationDone
                                        ? "border-zinc-700 bg-zinc-900/50 opacity-50"
                                        : "border-amber-700/60 bg-amber-950/20"
                                }`}>
                                    <div className="flex items-center gap-2">
                                        <span className="w-2 h-2 rounded-full bg-amber-400 shrink-0" />
                                        <p className="text-xs text-amber-400 font-medium uppercase tracking-wide">
                                            Action Requires Confirmation
                                        </p>
                                    </div>

                                    {msg.confirmationPayload && (
                                        <div className="text-xs text-zinc-400 space-y-1">
                                            <p>
                                                <span className="text-zinc-500">Action: </span>
                                                <span className="text-zinc-200 font-medium">{msg.confirmationPayload.tool_name}</span>
                                            </p>
                                            {Object.keys(msg.confirmationPayload.tool_params).length > 0 && (
                                                <p>
                                                    <span className="text-zinc-500">Parameters: </span>
                                                    <span className="text-zinc-300">
                                                        {JSON.stringify(msg.confirmationPayload.tool_params)}
                                                    </span>
                                                </p>
                                            )}
                                        </div>
                                    )}

                                    {!msg.confirmationDone ? (
                                        <div className="flex gap-2 pt-1">
                                            <Button
                                                onClick={() => handleConfirm(msg.pendingActionId!, true)}
                                                disabled={loading}
                                                size="sm"
                                                className="bg-blue-600 hover:bg-blue-500 text-white text-xs h-7 px-4"
                                            >
                                                Confirm
                                            </Button>
                                            <Button
                                                onClick={() => handleConfirm(msg.pendingActionId!, false)}
                                                disabled={loading}
                                                size="sm"
                                                variant="ghost"
                                                className="text-red-400 hover:text-red-300 hover:bg-zinc-800 text-xs h-7 px-4"
                                            >
                                                Cancel
                                            </Button>
                                        </div>
                                    ) : (
                                        <p className="text-xs text-zinc-500 italic">Response recorded.</p>
                                    )}
                                </div>
                            )}

                            {/* Citations */}
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
                <div className="flex gap-3 items-end">
                    <Textarea
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask about HR policies, employee info, compliance..."
                        rows={1}
                        className="flex-1 resize-none bg-zinc-900 border-zinc-700 text-white placeholder:text-zinc-600 focus-visible:ring-blue-500 rounded-xl"
                    />
                    <Button
                        onClick={() => submitQuery(query)}
                        disabled={loading || !query.trim()}
                        className="bg-blue-600 hover:bg-blue-500 text-white px-5 rounded-xl"
                    >
                        Send
                    </Button>
                </div>
                <p className="text-xs text-zinc-600 mt-2 text-center">Press Enter to send · Shift+Enter for new line</p>
            </div>
        </div>
    )
}
