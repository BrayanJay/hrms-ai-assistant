"use client"

import axios from "axios"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"

export default function LoginPage() {
    const router = useRouter()
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState("")
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
        e.preventDefault()
        setError("")
        setLoading(true)

        try {
            const response = await axios.post(
                `${process.env.NEXT_PUBLIC_BASE_HRIS_URL}/authenticate`,
                { username, password }
            )
            localStorage.setItem("access_token", response.data.access_token)
            localStorage.setItem("refresh_token", response.data.refresh_token)
            router.push("/documents")
        } catch (err) {
            if (axios.isAxiosError(err)) {
                setError(err.response?.data?.detail ?? "Invalid username or password.")
            } else {
                setError("An unexpected error occurred.")
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-zinc-950 px-4">
            <div className="w-full max-w-sm space-y-8">
                <div className="space-y-1">
                    <h1 className="text-2xl font-semibold tracking-tight text-white">
                        Astrynox <span className="text-blue-500">AI</span>
                    </h1>
                    <p className="text-sm text-zinc-400">Sign in with your HRIS credentials</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div className="space-y-2">
                        <Label htmlFor="username" className="text-zinc-300 text-sm">Username</Label>
                        <Input
                            id="username"
                            type="text"
                            placeholder="001234"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            className="bg-zinc-900 border-zinc-800 text-white placeholder:text-zinc-600 focus-visible:ring-blue-500"
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="password" className="text-zinc-300 text-sm">Password</Label>
                        <Input
                            id="password"
                            type="password"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            className="bg-zinc-900 border-zinc-800 text-white placeholder:text-zinc-600 focus-visible:ring-blue-500"
                        />
                    </div>

                    {error && <p className="text-sm text-red-400">{error}</p>}

                    <Button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium"
                    >
                        {loading ? "Signing in..." : "Sign in"}
                    </Button>
                </form>
            </div>
        </div>
    )
}
