import axios from "axios"

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_BASE_API_URL,
    withCredentials: true,
})

let isRefreshing = false
let failedQueue: { resolve: (value: unknown) => void; reject: (reason?: unknown) => void }[] = []

const processQueue = (error: unknown) => {
    failedQueue.forEach(({ resolve, reject }) => {
        if (error) reject(error)
        else resolve(undefined)
    })
    failedQueue = []
}

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config

        if (error.response?.status !== 401 || originalRequest._retry) {
            return Promise.reject(error)
        }

        if (isRefreshing) {
            return new Promise((resolve, reject) => {
                failedQueue.push({ resolve, reject })
            }).then(() => api(originalRequest))
              .catch((err) => Promise.reject(err))
        }

        originalRequest._retry = true
        isRefreshing = true

        try {
            await axios.post(
                `${process.env.NEXT_PUBLIC_BASE_API_URL}/api/auth/refresh`,
                {},
                { withCredentials: true }
            )
            processQueue(null)
            return api(originalRequest)
        } catch (refreshError) {
            processQueue(refreshError)
            if (typeof window !== "undefined") {
                window.location.href = "/auth/login"
            }
            return Promise.reject(refreshError)
        } finally {
            isRefreshing = false
        }
    }
)

export default api
