"use client"

import api from "@/lib/axios";
import axios from "axios";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect } from "react";

export default function GoogleCallbackPage() {
    const searchParams = useSearchParams()
    const router = useRouter()

    useEffect(() => {
        const code = searchParams.get("code")

        if (!code) {
            router.push("/auth/login")
            return
        }

        const handleCallback = async () => {
            try {
                await api.post("/auth/google", { code })
                router.push("/chat")
            } catch (err) {
                if (axios.isAxiosError(err)) {
                    router.push(`/auth/login?error=${err.response?.data?.detail ?? "Google login failed"}`)
                } else {
                    router.push("/auth/login?error=An unexpected error occurred")
                }
            }
        }
        handleCallback()
    }, [])

    return (
        <div className="min-h-screen flex items-center justify-center bg-zinc-950">
              <p className="text-zinc-400 text-sm">Completing Google sign in...</p>
          </div>
    )

}