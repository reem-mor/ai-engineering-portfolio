import type { ButtonHTMLAttributes, ReactNode } from "react";

export type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";

export type ButtonProps = {
  variant?: ButtonVariant;
  loading?: boolean;
  compact?: boolean;
  children: ReactNode;
} & Omit<ButtonHTMLAttributes<HTMLButtonElement>, "className">;

const variantClass: Record<ButtonVariant, string> = {
  primary: "btn--primary",
  secondary: "btn--secondary",
  ghost: "btn--ghost",
  danger: "btn--danger",
};

export function Button({
  variant = "primary",
  loading = false,
  compact = false,
  type = "button",
  children,
  disabled,
  ...rest
}: ButtonProps) {
  return (
    <button
      type={type}
      className={`btn ${variantClass[variant]}${compact ? " btn--compact" : ""}`}
      disabled={disabled || loading}
      {...rest}
    >
      {loading ? (
        <>
          <span className="loading-spin__ring" aria-hidden style={{ margin: 0, width: 18, height: 18, borderWidth: 2 }} />
          Loading
        </>
      ) : (
        children
      )}
    </button>
  );
}
