import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css" // Original globals.css import
import { cn } from "@/lib/utils" // cn utility for class names

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Оракул",
  description: "Интерфейс для Оракула Океана",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="ru">
      <body
        className={cn(
          inter.className,
          "bg-[#F0E0D0] text-[#333333]", // <--- Стили "Двача" применены здесь
        )}
        style={{ fontFamily: "Arial, Helvetica, sans-serif" }} // Дополнительно задаем шрифт напрямую
      >
        {children}
      </body>
    </html>
  )
}
