"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"

export default function ConfigurationsPage() {
    const [systemPrompt, setSystemPrompt] = useState(
        `Act as a HR and Compliance Assistant for Asia Asset Finance PLC internal employees.
Answer only based on the provided context. Do not hallucinate.
Only attribute information to a person if that person is explicitly named in the context chunk.
If a chunk does not mention a person by name, do not use it to describe that person.
Show inline citations for every claim [1], [2], [3].
If the context does not contain enough information to answer, say so.`
    )
    const [rewritePrompt, setRewritePrompt] = useState(
        `Rewrite the query to be specific and retrieval friendly.
Preserve the original content and do not use out of the topic words.
Return only the rewritten query, nothing else`
    )
    const [topK, setTopK] = useState("10")
    const [threshold, setThreshold] = useState("0.01")

    return (
        <div className="space-y-8 max-w-3xl">
            <div>
                <h2 className="text-xl font-semibold text-white">Configurations</h2>
                <p className="text-sm text-zinc-400 mt-1">System prompts and retrieval settings</p>
            </div>

            <div className="space-y-3">
                <Label className="text-zinc-300">LLM System Prompt</Label>
                <Textarea
                    value={systemPrompt}
                    onChange={(e) => setSystemPrompt(e.target.value)}
                    rows={8}
                    className="bg-zinc-900 border-zinc-700 text-white placeholder:text-zinc-600 focus-visible:ring-blue-500 font-mono text-sm resize-none"
                />
            </div>

            <div className="space-y-3">
                <Label className="text-zinc-300">Query Rewriter Prompt</Label>
                <Textarea
                    value={rewritePrompt}
                    onChange={(e) => setRewritePrompt(e.target.value)}
                    rows={4}
                    className="bg-zinc-900 border-zinc-700 text-white placeholder:text-zinc-600 focus-visible:ring-blue-500 font-mono text-sm resize-none"
                />
            </div>

            <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                    <Label className="text-zinc-300">Top K Chunks</Label>
                    <Input
                        value={topK}
                        onChange={(e) => setTopK(e.target.value)}
                        type="number"
                        className="bg-zinc-900 border-zinc-700 text-white focus-visible:ring-blue-500"
                    />
                </div>
                <div className="space-y-2">
                    <Label className="text-zinc-300">Retrieval Threshold</Label>
                    <Input
                        value={threshold}
                        onChange={(e) => setThreshold(e.target.value)}
                        type="number"
                        step="0.01"
                        className="bg-zinc-900 border-zinc-700 text-white focus-visible:ring-blue-500"
                    />
                </div>
            </div>

            <div className="pt-2">
                <Button disabled className="bg-blue-600 hover:bg-blue-500 text-white opacity-50 cursor-not-allowed">
                    Save Configuration (coming soon)
                </Button>
                <p className="text-xs text-zinc-600 mt-2">Configuration persistence via API coming in a future sprint</p>
            </div>
        </div>
    )
}
