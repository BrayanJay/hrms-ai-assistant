"use client"

import { useEffect, useState } from "react"

interface VectorConfig {
    size: number
    distance: string
}

interface Collection {
    name: string
    points_count: number
    vectors_count: number
    status: string
    vectors_config: Record<string, VectorConfig>
}

export default function QdrantPage() {
    const [collections, setCollections] = useState<Collection[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState("")

    useEffect(() => {
        const fetchCollections = async () => {
            try {
                const res = await fetch("http://localhost:6333/collections")
                const data = await res.json()

                const details = await Promise.all(
                    data.result.collections.map(async (c: { name: string }) => {
                        const detail = await fetch(`http://localhost:6333/collections/${c.name}`)
                        const d = await detail.json()
                        return {
                            name: c.name,
                            points_count: d.result.points_count,
                            vectors_count: d.result.vectors_count,
                            status: d.result.status,
                            vectors_config: d.result.config?.params?.vectors ?? {}
                        }
                    })
                )
                setCollections(details)
            } catch {
                setError("Failed to connect to Qdrant. Make sure it is running on port 6333.")
            } finally {
                setLoading(false)
            }
        }
        fetchCollections()
    }, [])

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-xl font-semibold text-white">Qdrant Collections</h2>
                <p className="text-sm text-zinc-400 mt-1">Vector database status and collection details</p>
            </div>

            {loading && <p className="text-sm text-zinc-500">Loading...</p>}
            {error && <p className="text-sm text-red-400">{error}</p>}

            {collections.map((col) => (
                <div key={col.name} className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-6 space-y-4">
                    <div className="flex items-center justify-between">
                        <h3 className="text-white font-medium">{col.name}</h3>
                        <span className={`px-2 py-1 rounded-md text-xs font-medium ${
                            col.status === "green"
                                ? "bg-green-500/10 text-green-400 border border-green-500/20"
                                : "bg-yellow-500/10 text-yellow-400 border border-yellow-500/20"
                        }`}>
                            {col.status}
                        </span>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-zinc-900 rounded-lg p-4">
                            <p className="text-xs text-zinc-500 mb-1">Points</p>
                            <p className="text-2xl font-semibold text-white">{col.points_count ?? 0}</p>
                        </div>
                        <div className="bg-zinc-900 rounded-lg p-4">
                            <p className="text-xs text-zinc-500 mb-1">Vectors</p>
                            <p className="text-2xl font-semibold text-white">{col.vectors_count ?? 0}</p>
                        </div>
                    </div>

                    {Object.keys(col.vectors_config).length > 0 && (
                        <div className="space-y-2">
                            <p className="text-xs text-zinc-500 uppercase tracking-wide">Vector Config</p>
                            <div className="grid grid-cols-2 gap-2">
                                {Object.entries(col.vectors_config).map(([name, config]) => (
                                    <div key={name} className="bg-zinc-900 rounded-md px-3 py-2 text-xs">
                                        <span className="text-blue-400 font-medium">{name}</span>
                                        <span className="text-zinc-400 ml-2">{config.size}d · {config.distance}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            ))}

            {!loading && collections.length === 0 && !error && (
                <div className="rounded-lg border border-zinc-800 py-12 text-center">
                    <p className="text-zinc-500 text-sm">No collections found</p>
                </div>
            )}
        </div>
    )
}
