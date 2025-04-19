"use client"

import { useState } from "react"
import { Sparkles, ArrowRight, Mail } from "lucide-react"
import { signInWithEmail, signInWithGoogle } from "@/server/auth/actions"
import Link from "next/link"

export default function LoginPage() {
  const [loginError, setLoginError] = useState("")

  const handleSubmit = async (formData: FormData) => {
    const result = await signInWithEmail({ message: "" }, formData)
    if (result.message) {
      setLoginError(result.message)
    }
  }

  return (
    <div className="min-h-screen bg-[#1A1A1A] flex flex-col items-center justify-center p-4">
      {/* Logo and header */}
      <div className="mb-8 text-center">
        <Link href="/">
          <h1 className="text-3xl font-semibold text-gray-200 mb-2">Graphis</h1>
        </Link>
        <div className="flex items-center justify-center gap-2">
          <Sparkles className="h-5 w-5 text-purple-400" />
          <p className="text-gray-400 text-sm">AI-powered assistant</p>
        </div>
      </div>

      {/* Login card */}
      <div className="w-full max-w-md bg-[#2A2A2A] rounded-lg border border-gray-700 p-6 shadow-xl">
        <h2 className="text-xl font-medium text-gray-200 mb-6">Welcome back</h2>

        {loginError && (
          <div className="mb-4 p-3 bg-red-900/30 border border-red-800 rounded text-red-200 text-sm">
            {loginError}
          </div>
        )}

        {/* Google login button */}
        <div className="mb-6">
          <button
            onClick={() => signInWithGoogle()}
            className="w-full bg-white hover:bg-gray-100 text-gray-800 font-medium py-2 px-4 rounded-md flex items-center justify-center gap-2 transition-colors"
          >
            <svg className="h-5 w-5" viewBox="0 0 24 24">
              <path
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                fill="#4285F4"
              />
              <path
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                fill="#34A853"
              />
              <path
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"
                fill="#FBBC05"
              />
              <path
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                fill="#EA4335"
              />
            </svg>
            Sign in with Google
          </button>
        </div>

        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-600"></div>
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-[#2A2A2A] px-2 text-gray-400">Or continue with</span>
          </div>
        </div>

        <form action={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="email" className="block text-sm font-medium text-gray-300">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              className="w-full px-3 py-2 bg-[#333333] border border-gray-600 rounded-md text-gray-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="you@example.com"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="block text-sm font-medium text-gray-300">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              className="w-full px-3 py-2 bg-[#333333] border border-gray-600 rounded-md text-gray-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="••••••••"
            />
          </div>

          <div className="pt-2">
            <button
              type="submit"
              className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-md flex items-center justify-center gap-2 transition-colors"
            >
              Sign in
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-400">
            Don't have an account?
            <Link
              href="/register"
              className="ml-2 text-purple-400 hover:text-purple-300 focus:outline-none"
            >
              Sign up
            </Link>
          </p>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-8 text-center">
        <p className="text-xs text-gray-500">
          By continuing, you agree to Graphis's{" "}
          <Link href="#" className="text-gray-400 hover:text-gray-300">
            Terms of Service
          </Link>{" "}
          and{" "}
          <Link href="#" className="text-gray-400 hover:text-gray-300">
            Privacy Policy
          </Link>
        </p>
      </div>
    </div>
  )
}