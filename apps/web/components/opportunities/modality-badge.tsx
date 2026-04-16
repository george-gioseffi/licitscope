import { Badge } from "@/components/ui/badge";

const LABELS: Record<string, { label: string; tone: "brand" | "amber" | "rose" | "mint" | "violet" | "default" }> = {
  pregao_eletronico: { label: "Pregão Eletrônico", tone: "brand" },
  pregao_presencial: { label: "Pregão Presencial", tone: "brand" },
  concorrencia: { label: "Concorrência", tone: "violet" },
  tomada_de_precos: { label: "Tomada de Preços", tone: "violet" },
  convite: { label: "Convite", tone: "violet" },
  concurso: { label: "Concurso", tone: "default" },
  leilao: { label: "Leilão", tone: "default" },
  dialogo_competitivo: { label: "Diálogo Competitivo", tone: "violet" },
  dispensa: { label: "Dispensa", tone: "amber" },
  inexigibilidade: { label: "Inexigibilidade", tone: "rose" },
  credenciamento: { label: "Credenciamento", tone: "mint" },
  outros: { label: "Outros", tone: "default" },
};

export function ModalityBadge({ value }: { value: string }) {
  const info = LABELS[value] ?? { label: value, tone: "default" as const };
  return <Badge tone={info.tone}>{info.label}</Badge>;
}

const STATUS_LABELS: Record<string, { label: string; tone: "mint" | "amber" | "rose" | "default" | "brand" | "violet" }> = {
  published: { label: "Divulgada", tone: "brand" },
  open: { label: "Aberta", tone: "mint" },
  proposals_received: { label: "Propostas recebidas", tone: "brand" },
  under_analysis: { label: "Em análise", tone: "amber" },
  awarded: { label: "Homologada", tone: "violet" },
  contracted: { label: "Contratada", tone: "violet" },
  cancelled: { label: "Cancelada", tone: "rose" },
  deserted: { label: "Deserta", tone: "rose" },
  closed: { label: "Encerrada", tone: "default" },
  draft: { label: "Rascunho", tone: "default" },
};

export function StatusBadge({ value }: { value: string }) {
  const info = STATUS_LABELS[value] ?? { label: value, tone: "default" as const };
  return <Badge tone={info.tone}>{info.label}</Badge>;
}
