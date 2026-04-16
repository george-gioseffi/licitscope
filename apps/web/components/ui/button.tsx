import { ButtonHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

type Variant = "primary" | "ghost" | "outline" | "danger";
type Size = "sm" | "md" | "lg";

const VARIANTS: Record<Variant, string> = {
  primary:
    "bg-brand-600 hover:bg-brand-500 text-white shadow-glow ring-1 ring-brand-400/40 disabled:opacity-50",
  ghost: "bg-transparent text-ink-200 hover:bg-ink-800",
  outline:
    "bg-transparent text-ink-100 ring-1 ring-ink-700 hover:bg-ink-800 hover:ring-ink-600",
  danger: "bg-rose-600 hover:bg-rose-500 text-white",
};

const SIZES: Record<Size, string> = {
  sm: "h-8 px-3 text-xs",
  md: "h-9 px-4 text-sm",
  lg: "h-10 px-5 text-sm",
};

export const Button = forwardRef<
  HTMLButtonElement,
  ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; size?: Size }
>(({ variant = "primary", size = "md", className, ...props }, ref) => (
  <button
    ref={ref}
    className={cn(
      "inline-flex items-center justify-center gap-2 rounded-md font-medium transition",
      "focus-visible:outline-none disabled:cursor-not-allowed",
      VARIANTS[variant],
      SIZES[size],
      className,
    )}
    {...props}
  />
));
Button.displayName = "Button";
