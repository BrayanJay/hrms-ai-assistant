"use client"

import { useEffect, useState } from "react"
import api from "@/lib/axios"

interface Summary {
    total_queries: number
    cache_hit_rate: number
    avg_response_time_ms: number
}

interface DailyEntry {
    date: string
    count: number
}

interface TopQuery {
    query: string
    count: number
}

export default function AccuracyPage() {
    const [summary, setSummary] = useState<Summary | null>(null)
    const [daily, setDaily] = useState<DailyEntry[]>([])
    const [topQueries, setTopQueries] = useState<TopQuery[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState("")

    useEffect(() => {
        const fetchAll = async () => {
            try {
                const [summaryRes, dailyRes, topRes] = await Promise.all([
                    api.get("/analytics/"),
                    api.get("/analytics/daily"),
                    api.get("/analytics/top-queries"),
                ])
                setSummary(summaryRes.data)
                setDaily(dailyRes.data)
                setTopQueries(topRes.data)
            } catch {
                setError("Failed to load analytics data.")
            } finally {
                setLoading(false)
            }
        }
        fetchAll()
    }, [])

    if (loading) return <p className="text-sm text-zinc-500">Loading...</p>
    if (error) return <p className="text-sm text-red-400">{error}</p>

    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-xl font-semibold text-white">Analytics</h2>
                <p className="text-sm text-zinc-400 mt-1">Query volume, cache performance, and usage patterns</p>
            </div>

            {/* Summary cards */}
            <div className="grid grid-cols-3 gap-4">
                <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-5">
                    <p className="text-xs text-zinc-500 mb-1">Total Queries</p>
                    <p className="text-3xl font-semibold text-white">{summary?.total_queries ?? 0}</p>
                </div>
                <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-5">
                    <p className="text-xs text-zinc-500 mb-1">Cache Hit Rate</p>
                    <p className="text-3xl font-semibold text-white">
                        {summary?.cache_hit_rate != null ? `${summary.cache_hit_rate}%` : "—"}
                    </p>
                </div>
                <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-5">
                    <p className="text-xs text-zinc-500 mb-1">Avg Response Time</p>
                    <p className="text-3xl font-semibold text-white">
                        {summary?.avg_response_time_ms != null ? `${summary.avg_response_time_ms}ms` : "—"}
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
                {/* Daily volume */}
                <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-5 space-y-4">
                    <p className="text-sm font-medium text-white">Daily Query Volume (Last 7 Days)</p>
                    {daily.length === 0 ? (
                        <p className="text-xs text-zinc-600">No data yet</p>
                    ) : (
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="text-left text-xs text-zinc-500 border-b border-zinc-800">
                                    <th className="pb-2">Date</th>
                                    <th className="pb-2 text-right">Queries</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-zinc-800">
                                {daily.map((row) => (
                                    <tr key={row.date}>
                                        <td className="py-2 text-zinc-400">{row.date}</td>
                                        <td className="py-2 text-right text-white font-medium">{row.count}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>

                {/* Top queries */}
                <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-5 space-y-4">
                    <p className="text-sm font-medium text-white">Top Queries</p>
                    {topQueries.length === 0 ? (
                        <p className="text-xs text-zinc-600">No data yet</p>
                    ) : (
                        <ol className="space-y-2">
                            {topQueries.map((q, i) => (
                                <li key={i} className="flex items-start gap-3">
                                    <span className="text-xs text-zinc-600 w-4 mt-0.5">{i + 1}</span>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-xs text-zinc-300 truncate">{q.query}</p>
                                    </div>
                                    <span className="text-xs text-zinc-500 shrink-0">{q.count}×</span>
                                </li>
                            ))}
                        </ol>
                    )}
                </div>
            </div>
        </div>
    )
}
