type LoadingSpinnerProps = { label?: string };

export function LoadingSpinner({ label = "Loading" }: LoadingSpinnerProps) {
  return (
    <div className="loading-spin" role="status" aria-live="polite">
      <span className="loading-spin__ring" aria-hidden />
      <span>{label}</span>
    </div>
  );
}
