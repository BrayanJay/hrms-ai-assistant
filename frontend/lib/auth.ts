import api from "./axios"

export const logout = async () => {
    await api.post("/api/auth/logout")
}