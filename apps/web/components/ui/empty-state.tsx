import { ReactNode } from "react";

export function EmptyState({
  icon,
  title,
  description,
  action,
}: {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-ink-700 bg-ink-900/60 p-10 text-center">
      {icon && <div className="text-ink-400">{icon}</div>}
      <div>
        <div className="text-sm font-medium text-ink-100">{title}</div>
        {description && <div className="mt-1 text-xs text-ink-400">{description}</div>}
      </div>
      {action}
    </div>
  );
}
