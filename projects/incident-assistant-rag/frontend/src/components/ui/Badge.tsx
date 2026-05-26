import type { ReactNode } from "react";

export type BadgeVariant = "neutral" | "success" | "warning" | "danger" | "info";

export type BadgeProps = {
  variant?: BadgeVariant;
  outline?: boolean;
  classNameExtra?: string;
  /** When set, overrides `variant` with a custom palette class (e.g. severity-critical). */
  paletteClass?: string;
  children: ReactNode;
};

const map: Record<BadgeVariant, string> = {
  neutral: "badge--neutral",
  success: "badge--success",
  warning: "badge--warning",
  danger: "badge--danger",
  info: "badge--info",
};

export function Badge({ variant = "neutral", outline = false, classNameExtra = "", paletteClass, children }: BadgeProps) {
  const tone = paletteClass ?? map[variant];
  return (
    <span className={`badge ${tone}${outline ? " badge--outline" : ""} ${classNameExtra}`.trim()}>{children}</span>
  );
}
