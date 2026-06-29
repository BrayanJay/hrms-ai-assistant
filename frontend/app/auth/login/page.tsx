"use client"

import axios from "axios"
import { useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import Link from "next/link"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import api from "@/lib/axios"
import GoogleLoginBtn from "@/components/auth/googleLoginBtn"

export default function LoginPage() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const [email, setEmail] = useState(searchParams.get("email") ?? "")
    const [password, setPassword] = useState("")
    const [error, setError] = useState("")
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError("")
        setLoading(true)

        try {
            await api.post("/auth/login", { email, password })
            router.push(`/auth/chat`)
        } catch (err) {
            if (axios.isAxiosError(err)) {
                setError(err.response?.data?.detail ?? "Registration failed. Please try again.")
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
                    <p className="text-sm text-zinc-400">Welcome back</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div className="space-y-2">
                        <Label htmlFor="email" className="text-zinc-300 text-sm">Work email</Label>
                        <Input
                            id="email"
                            type="email"
                            placeholder="you@company.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
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
                        {loading ? "Login to account..." : "Login"}
                    </Button>
                </form>

                <p className="text-sm text-zinc-500 text-center">
                    Don&apos;t have an account?{" "}
                    <Link href="/auth/register" className="text-blue-400 hover:text-blue-300 transition-colors">
                        Register
                    </Link>
                </p>

                <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-zinc-800" />
                    </div>
                    <div className="relative flex justify-center text-xs text-zinc-500">
                        <span className="bg-zinc-950 px-2">or</span>
                    </div>
                </div>

                <div className="space-y-2">
                    <GoogleLoginBtn/>
                </div>
                
            </div>
        </div>
    )
}
