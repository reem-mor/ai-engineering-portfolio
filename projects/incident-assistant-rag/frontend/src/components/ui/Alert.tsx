import type { ReactNode } from "react";

export type AlertVariant = "success" | "error" | "warning" | "info";

export type AlertProps = {
  variant: AlertVariant;
  title?: string;
  children: ReactNode;
};

const variantMap: Record<AlertVariant, string> = {
  success: "alert--success",
  error: "alert--error",
  warning: "alert--warning",
  info: "alert--info",
};

export function Alert({ variant, title, children }: AlertProps) {
  const role = variant === "error" ? "alert" : "status";

  return (
    <div className={`alert ${variantMap[variant]}`} role={role}>
      {title ? <p className="alert__title">{title}</p> : null}
      <div className="alert__body">{children}</div>
    </div>
  );
}
