 "use client"

  import Link from "next/link"
  import { useRouter } from "next/navigation"
  import { FileText, LogOut } from "lucide-react"
  import api from "@/lib/axios"

  export default function AdminLayout({ children }: { children: React.ReactNode }) {
      const router = useRouter()

      const handleLogout = async () => {
          try {
              await api.post("/auth/logout")
          } finally {
              router.push("/auth/login")
          }
      }

      return (
          <div className="min-h-screen flex bg-zinc-950">
              {/* Sidebar */}
              <aside className="w-64 flex flex-col border-r border-zinc-800 px-4 py-6">
                  <div className="mb-8">
                      <h1 className="text-lg font-semibold text-white">
                          Astrynox <span className="text-blue-500">AI</span>
                      </h1>
                      <p className="text-xs text-zinc-500 mt-1">Admin Dashboard</p>
                  </div>

                  <nav className="flex-1 space-y-1">
                      <Link
                          href="/admin/documents"
                          className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-zinc-400 hover:text-white
  hover:bg-zinc-800 transition-colors"
                      >
                          <FileText size={16} />
                          Documents
                      </Link>
                  </nav>

                  <button
                      onClick={handleLogout}
                      className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-zinc-400 hover:text-red-400
  hover:bg-zinc-800 transition-colors"
                  >
                      <LogOut size={16} />
                      Logout
                  </button>
              </aside>

              {/* Main content */}
              <main className="flex-1 p-8">
                  {children}
              </main>
          </div>
      )
  }