"use client";

import { ReactNode, useState } from "react";

export function Tooltip({ content, children }: { content: ReactNode; children: ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <span
      className="relative inline-flex"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      {children}
      {open && (
        <span className="pointer-events-none absolute bottom-full left-1/2 z-10 mb-2 -translate-x-1/2 whitespace-nowrap rounded-md bg-ink-800 px-2 py-1 text-[11px] text-ink-100 ring-1 ring-ink-700 shadow">
          {content}
        </span>
      )}
    </span>
  );
}
