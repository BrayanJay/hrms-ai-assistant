"use client"
import GoogleLoginBtn from "@/components/auth/googleLoginBtn"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import api from "@/lib/axios"
import axios from "axios"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useState } from "react"

export default function RegisterPage () {
    const router = useRouter()
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [confirmPassword, setConfirmPassword] = useState("")
    const [error, setError] = useState("")
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError("")
        setLoading(true)

        try {
            if (password !== confirmPassword) {
                setError("Passwords do not match")
                setLoading(false)
                return
            }

            await api.post("/auth/register", {email, password})
            router.push(`/auth/verify-otp?email=${encodeURIComponent(email)}`)
        } catch (err) {
            if (axios.isAxiosError(err)) {
                setError(err.response?.data?.detail ?? "Registration failed. Please try again.")
            } else {
                setError("An Unexpected error occured.")
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
                <p className="text-sm text-zinc-400">Create your account to get started</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div className="space-y-2">
                        <Label htmlFor="email" className="text-zinc-300 text-sm">Work Email</Label>
                        <Input id="email" type="email" placeholder="you@company.com" value={email} onChange={(e) => setEmail(e.target.value)} required
                        className="bg-zinc-900 border-zinc-800 text-white placeholder:text-zinc-600 focus-visible:ring-blue-500"
                        />
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="password" className="text-zinc-300 text-sm">Create Password</Label>
                        <Input id="password" type="password" placeholder="********" value={password} onChange={(e) => setPassword(e.target.value)} required
                        className="bg-zinc-900 border-zinc-800 text-white placeholder:text-zinc-600 focus-visible:ring-blue-500"
                        />
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="confirmPassword" className="text-zinc-300 text-sm">Confirm Password</Label>
                        <Input id="confirmPassword" type="password" placeholder="********" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required
                        className="bg-zinc-900 border-zinc-800 text-white placeholder:text-zinc-600 focus-visible:ring-blue-500"
                        />
                    </div>
                    {error && <p className="text-sm text-red-400">{error}</p>}
                    <Button type="submit" disabled={loading}
                    className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium">
                        {loading ? "Creating Account..." : "Create Account"}
                    </Button>
                </form>

                <p className="text-sm text-zinc-500 text-center">
                    Already have an account?{" "}
                    <Link href="/auth/login" className="text-blue-400 hover:text-blue-300 transition-colors">
                    Login
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
