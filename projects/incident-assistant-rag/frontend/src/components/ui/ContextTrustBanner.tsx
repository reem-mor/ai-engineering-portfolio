import { KB_EXPAND_NO_MATCH_HINT, KB_NO_CONTEXT_HINT, trustBannerTitle } from "../../utils/ragDisplay";

export type ContextTrustBannerProps = {
  usedContext: boolean;
  confidence: string;
};

function TrustIcon({ variant }: { variant: "grounded" | "no-match" | "low" }) {
  if (variant === "grounded") {
    return (
      <svg className="trust-banner__icon" width={20} height={20} viewBox="0 0 24 24" fill="none" aria-hidden>
        <path d="M9 12l2 2 4-4" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
        <path
          d="M12 3l8 4v6c0 5-3.5 8-8 8s-8-3-8-8V7l8-4z"
          stroke="currentColor"
          strokeWidth={1.6}
          strokeLinejoin="round"
        />
      </svg>
    );
  }
  if (variant === "no-match") {
    return (
      <svg className="trust-banner__icon" width={20} height={20} viewBox="0 0 24 24" fill="none" aria-hidden>
        <path d="M12 8v5M12 17h0" stroke="currentColor" strokeWidth={2} strokeLinecap="round" />
        <path
          d="M10.29 4.58L3.82 17.4a2 2 0 001.71 3h13.93a2 2 0 001.71-3L13.71 4.58a2 2 0 00-3.42 0z"
          stroke="currentColor"
          strokeWidth={1.6}
          strokeLinejoin="round"
        />
      </svg>
    );
  }
  return (
    <svg className="trust-banner__icon" width={20} height={20} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M12 8v5M12 17h0" stroke="currentColor" strokeWidth={2} strokeLinecap="round" />
      <circle cx={12} cy={12} r={9} stroke="currentColor" strokeWidth={1.6} />
    </svg>
  );
}

export function ContextTrustBanner({ usedContext, confidence }: ContextTrustBannerProps) {
  const title = trustBannerTitle(usedContext, confidence);
  const variant = !usedContext ? "no-match" : confidence.toLowerCase() === "low" ? "low" : "grounded";

  return (
    <div className={`trust-banner trust-banner--${variant}`} role="status" aria-live="polite">
      <div className="trust-banner__head">
        <TrustIcon variant={variant} />
        <p className="trust-banner__title">{title}</p>
      </div>
      {!usedContext ? (
        <>
          <p className="trust-banner__body">{KB_NO_CONTEXT_HINT}</p>
          <p className="trust-banner__body trust-banner__body--emphasis">{KB_EXPAND_NO_MATCH_HINT}</p>
        </>
      ) : null}
      {usedContext && confidence.toLowerCase() === "low" ? (
        <p className="trust-banner__body">
          Similarity scores are weak. Treat retrieved excerpts as hints—confirm with logs, dashboards, and on-call
          runbooks before escalation.
        </p>
      ) : null}
      {usedContext && confidence.toLowerCase() !== "low" ? (
        <p className="trust-banner__body">
          Generated only from the evidence chunks listed below. The model is instructed not to invent commands, owners, or
          procedures outside that context.
        </p>
      ) : null}
    </div>
  );
}
