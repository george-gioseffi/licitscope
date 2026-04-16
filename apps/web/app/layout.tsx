import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";
import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";

export const metadata: Metadata = {
  title: "LicitScope — Procurement Intelligence for Brazil",
  description:
    "Explainable procurement intelligence for Brazilian public procurement data. Live PNCP ingestion, rule-based enrichment, TF-IDF semantic search, and pricing anomaly signals.",
  applicationName: "LicitScope",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className="dark">
      <body className="min-h-screen bg-ink-900 text-ink-50 antialiased">
        <Providers>
          <div className="flex min-h-screen">
            <Sidebar />
            <div className="flex min-w-0 flex-1 flex-col">
              <Topbar />
              <main className="flex-1 bg-[radial-gradient(60%_40%_at_50%_0%,rgba(43,101,245,0.08),transparent)]">
                <div className="mx-auto w-full max-w-[1440px] px-6 py-8">{children}</div>
              </main>
              <footer className="border-t border-ink-800 px-6 py-4 text-xs text-ink-400">
                <div className="mx-auto flex w-full max-w-[1440px] items-center justify-between">
                  <span>
                    LicitScope · dados públicos via PNCP, Portal da Transparência e Compras.gov.br
                  </span>
                  <span>Demo build · portfolio only</span>
                </div>
              </footer>
            </div>
          </div>
        </Providers>
      </body>
    </html>
  );
}
