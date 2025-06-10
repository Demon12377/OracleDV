"use client"

import type React from "react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2, MessageSquareText, AlertTriangle } from "lucide-react"

interface OracleResponse {
  intent: string
  crystal: string
  meditation_time_sec: number
}

interface OracleError {
  error: string
}

export default function OraclePageDvach() {
  const [intent, setIntent] = useState<string>("")
  const [result, setResult] = useState<OracleResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!intent.trim()) {
      setError("Анон, введи что-нибудь в поле интента.")
      return
    }

    setIsLoading(true)
    setResult(null)
    setError(null)

    try {
      const response = await fetch("/api/oracle", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ intent }),
      })

      const data = await response.json()

      if (!response.ok) {
        const errorData = data as OracleError
        throw new Error(
          errorData.error ||
            `Ошибка сервера: ${response.status}. Попробуй еще раз или проверь логи, если ты админ этой борды.`,
        )
      }

      setResult(data as OracleResponse)
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError("Неизвестная ошибка. Возможно, Оракул сегодня не в духе.")
      }
      console.error("Ошибка при обращении к Оракулу:", err)
    } finally {
      setIsLoading(false)
    }
  }

  // Стили для ссылок теперь нужно будет применять индивидуально или через компоненты,
  // так как глобальный стиль для 'a' убран из globals.css для теста.
  // Например, можно создать компонент <StyledLink> или использовать классы Tailwind.

  return (
    <div className="min-h-screen flex flex-col items-center justify-start pt-10 px-4">
      {" "}
      {/* Удален font-family отсюда, т.к. он в layout.tsx */}
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-bold text-[#800000]">Оракул/b/</h1>
        <p className="text-sm text-[#4F4F4F]">Задай свой вопрос Океану Смыслов</p>
      </header>
      <Card className="w-full max-w-2xl bg-[#EEAA88] border border-[#D96F00] shadow-md rounded-sm">
        <CardHeader className="bg-[#D96F00] p-2 rounded-t-sm">
          <CardTitle className="text-sm font-bold text-white">Новый пост Оракулу</CardTitle>
        </CardHeader>
        <CardContent className="p-4 space-y-4">
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label htmlFor="intent" className="block text-xs font-semibold text-[#333333] mb-1">
                Твой интент, Анон:
              </label>
              <Textarea
                id="intent"
                value={intent}
                onChange={(e) => setIntent(e.target.value)}
                placeholder="Например: В чем смысл /b/?"
                className="w-full p-2 border border-[#B8A088] rounded-sm bg-[#FFFEEF] focus:ring-1 focus:ring-[#D96F00] focus:border-[#D96F00] text-sm"
                rows={4}
                required
              />
            </div>
            <Button
              type="submit"
              className="bg-[#D96F00] hover:bg-[#FF8000] text-white font-semibold py-2 px-4 border border-[#B85C00] rounded-sm text-sm shadow-sm"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Оракул медитирует...
                </>
              ) : (
                "Спросить"
              )}
            </Button>
          </form>

          {error && (
            <div className="mt-4 p-3 bg-[#FFD1D1] border border-[#CC0000] rounded-sm text-[#800000] text-sm">
              <div className="flex items-center">
                <AlertTriangle className="h-5 w-5 mr-2" />
                <strong>Ошибка Оракула:</strong>
              </div>
              <p className="mt-1">{error}</p>
            </div>
          )}

          {result && (
            <div className="mt-6">
              <div className="bg-[#D9CCBB] p-2 rounded-t-sm border-b border-[#B8A088]">
                <h3 className="text-xs font-bold text-[#333333]">
                  <MessageSquareText className="inline h-4 w-4 mr-1" />
                  Ответ Оракула на интент: <span className="italic">{result.intent}</span>
                </h3>
                <p className="text-xs text-[#4F4F4F]">Время медитации: {result.meditation_time_sec} сек.</p>
              </div>
              <div className="p-4 bg-[#FFFEEF] border border-t-0 border-[#B8A088] rounded-b-sm">
                <p className="text-sm whitespace-pre-wrap leading-relaxed">{result.crystal}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
      <footer className="mt-10 text-center text-xs text-[#4F4F4F]">
        <p>Это экспериментальный Оракул. Не принимайте его предсказания слишком близко к сердцу.</p>
        <p>Стиль вдохновлен Двачем, но это не он.</p>
      </footer>
    </div>
  )
}
