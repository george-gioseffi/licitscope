import Link from "next/link";
import { ArrowRight, Database, Sparkles, Telescope } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function AboutPage() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Sobre o projeto"
        title="O que é LicitScope"
        description="Uma plataforma open-source de inteligência para compras públicas brasileiras — feita para reduzir o esforço de leitura de editais, cruzar histórico de preços e ampliar a transparência."
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database size={14} /> Fontes de dados
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-2 text-sm text-ink-200">
            <p>
              LicitScope integra-se com as principais fontes públicas brasileiras de compras:
            </p>
            <ul className="mt-2 flex flex-col gap-2">
              <li className="flex items-center gap-2">
                <Badge tone="brand">PNCP</Badge>
                <span className="text-[13px]">Portal Nacional de Contratações Públicas</span>
              </li>
              <li className="flex items-center gap-2">
                <Badge tone="violet">Transparência</Badge>
                <span className="text-[13px]">Portal da Transparência (roteiro)</span>
              </li>
              <li className="flex items-center gap-2">
                <Badge tone="mint">Compras.gov</Badge>
                <span className="text-[13px]">Compras.gov.br (roteiro)</span>
              </li>
            </ul>
            <p className="mt-3 text-xs text-ink-400">
              Onde as integrações ao vivo são instáveis, caímos em snapshots determinísticos em
              <code className="mx-1 rounded bg-ink-800 px-1">data-demo/</code> para garantir uma demo
              confiável ponta-a-ponta.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles size={14} /> Camada de IA
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-3 text-sm text-ink-200">
            <p>
              A camada de enriquecimento combina regras determinísticas com heurísticas NLP leves,
              sem exigir LLMs externos:
            </p>
            <ul className="list-disc pl-5 text-[13px] text-ink-300">
              <li>Taxonomia editável (TI, Saúde, Obras, Segurança, …)</li>
              <li>Resumo e tópicos a partir de regras lexicais</li>
              <li>TF-IDF hasheado para busca semântica + similaridade</li>
              <li>Scores explicáveis de complexidade, esforço e risco</li>
              <li>Heurística de dispersão de preços por CATMAT/CATSER</li>
            </ul>
            <p className="mt-1 text-xs text-ink-400">
              Um <code className="rounded bg-ink-800 px-1">Provider</code> abstrato permite plugar
              qualquer LLM externo quando disponível (Anthropic, OpenAI, Ollama).
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Telescope size={14} /> Para quem é
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-2 text-sm text-ink-200">
            <ul className="list-disc pl-5 text-[13px] text-ink-300">
              <li>Empresas B2G buscando oportunidades relevantes sem ruído</li>
              <li>Jornalistas de dados investigando padrões de contratação</li>
              <li>Órgãos de controle cruzando preços e sinais de risco</li>
              <li>Pesquisadores em transparência e dados abertos</li>
            </ul>
            <p className="mt-2 text-xs text-ink-400">
              O projeto é portfólio open-source com licença MIT — qualquer instituição pode
              adaptar. Veja o README para roadmap, limitações e notas éticas.
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Como começar a explorar</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 text-sm md:grid-cols-3">
          <Link
            href="/"
            className="group rounded-lg border border-ink-800 bg-ink-900/60 p-4 hover:border-brand-500/40"
          >
            <div className="mb-1 text-ink-100">1. Dashboard</div>
            <div className="text-[12px] text-ink-400">
              Visão consolidada de publicações, categorias, geografia e órgãos.
            </div>
            <div className="mt-2 inline-flex items-center gap-1 text-brand-300 group-hover:text-brand-200">
              Abrir <ArrowRight size={12} />
            </div>
          </Link>
          <Link
            href="/opportunities"
            className="group rounded-lg border border-ink-800 bg-ink-900/60 p-4 hover:border-brand-500/40"
          >
            <div className="mb-1 text-ink-100">2. Licitações</div>
            <div className="text-[12px] text-ink-400">
              Filtre por estado, modalidade, valor e categoria; abra detalhes com resumo de IA.
            </div>
            <div className="mt-2 inline-flex items-center gap-1 text-brand-300 group-hover:text-brand-200">
              Abrir <ArrowRight size={12} />
            </div>
          </Link>
          <Link
            href="/contracts"
            className="group rounded-lg border border-ink-800 bg-ink-900/60 p-4 hover:border-brand-500/40"
          >
            <div className="mb-1 text-ink-100">3. Contratos & preços</div>
            <div className="text-[12px] text-ink-400">
              Consulte dispersão de preços por CATMAT e histórico de contratos.
            </div>
            <div className="mt-2 inline-flex items-center gap-1 text-brand-300 group-hover:text-brand-200">
              Abrir <ArrowRight size={12} />
            </div>
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
