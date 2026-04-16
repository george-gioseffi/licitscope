import { ReactNode } from "react";

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="mb-6 flex flex-col gap-3 border-b border-ink-800 pb-6 md:flex-row md:items-end md:justify-between">
      <div>
        {eyebrow && (
          <div className="mb-1 text-[11px] uppercase tracking-widest text-brand-300">
            {eyebrow}
          </div>
        )}
        <h1 className="text-[22px] font-semibold tracking-tight text-ink-50">{title}</h1>
        {description && (
          <p className="mt-1 max-w-2xl text-sm text-ink-300">{description}</p>
        )}
      </div>
      {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
    </div>
  );
}
