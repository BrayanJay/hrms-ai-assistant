"use client"

export default function AccuracyPage() {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-xl font-semibold text-white">Accuracy Monitoring</h2>
                <p className="text-sm text-zinc-400 mt-1">Track answer quality and model performance</p>
            </div>
            <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 flex items-center justify-center" style={{ height: "calc(100vh - 200px)" }}>
                <div className="text-center space-y-2">
                    <p className="text-zinc-400 text-sm">Accuracy monitoring coming soon</p>
                    <p className="text-zinc-600 text-xs">Will display per-session accuracy scores and trends</p>
                </div>
            </div>
        </div>
    )
}
