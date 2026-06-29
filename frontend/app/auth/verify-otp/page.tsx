"use client"

import axios from "axios"
import { useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import Link from "next/link"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import api from "@/lib/axios"

export default function VerifyOTPPage() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const [email, setEmail] = useState(searchParams.get("email") ?? "")
    const [otp, setOtp] = useState(["", "", "", "", "", ""])
    const [error, setError] = useState("")
    const [loading, setLoading] = useState(false)

    const handleChange = (index: number, value: string) => {
        if (!/^\d*$/.test(value)) return
        const newOtp = [...otp]
        newOtp[index] = value.slice(-1)
        setOtp(newOtp)

        if (value && index < 5) {
            document.getElementById(`otp-${index + 1}`)?.focus()
        }
    }

    const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
        if (e.key === "Backspace" && !otp[index] && index > 0) {
            document.getElementById(`otp-${index - 1}`)?.focus()
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError("")
        setLoading(true)

        try {
            await api.post("/auth/verify-otp", { email, otp: otp.join("") })
            router.push(`/chat`)
        } catch (err) {
            if (axios.isAxiosError(err)) {
                setError(err.response?.data?.detail ?? "Authentication failed. Please try again.")
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
                        Check your <span className="text-blue-500">email</span>
                    </h1>
                    <p className="text-sm text-zinc-400">Please enter the 6-digit verification code we sent to 
                        <br></br><span className="text-blue-500">{email}</span>
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div className="flex gap-3 justify-center">
                        {otp.map((digit, i) => (
                            <Input
                                key={i}
                                id={`otp-${i}`}
                                type="text"
                                inputMode="numeric"
                                maxLength={1}
                                value={digit}
                                onChange={(e) => handleChange(i, e.target.value)}
                                onKeyDown={(e) => handleKeyDown(i, e)}
                                className="w-12 h-12 text-center text-xl bg-zinc-900 border-zinc-800 text-white"
                            />
                        ))}
                    </div>

                    {error && <p className="text-sm text-red-400">{error}</p>}

                    <Button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium"
                    >
                        {loading ? "verifying..." : "Verify"}
                    </Button>
                </form>

                <p className="text-sm text-zinc-500 text-center">
                    OTP not recieved?{" "}
                    <Link href={`/auth/login?email=${email}`} className="text-blue-400 hover:text-blue-300 transition-colors">
                        Resend OTP
                    </Link>
                </p>
            </div>
        </div>
    )
}
