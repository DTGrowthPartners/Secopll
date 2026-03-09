import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "SECOP Monitor — DT Growth Partners",
  description:
    "Dashboard de monitoreo de contratos SECOP para identificar oportunidades de negocio",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className="dark">
      <body className="min-h-screen bg-[#0a0a0a] text-[#ededed] antialiased">
        <Providers>
          <header className="sticky top-0 z-50 border-b border-[#262626] bg-[#0a0a0a]/80 backdrop-blur-sm">
            <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4">
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold text-brand-blue">
                  SECOP Monitor
                </span>
                <span className="text-xs text-[#a3a3a3]">
                  by DT Growth Partners
                </span>
              </div>
              <nav className="flex items-center gap-4 text-sm">
                <a href="/" className="text-[#ededed] hover:text-brand-blue">
                  Dashboard
                </a>
                <a
                  href="/settings"
                  className="text-[#a3a3a3] hover:text-brand-blue"
                >
                  Configuracion
                </a>
              </nav>
            </div>
          </header>
          <main className="mx-auto max-w-7xl px-4 py-6">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
