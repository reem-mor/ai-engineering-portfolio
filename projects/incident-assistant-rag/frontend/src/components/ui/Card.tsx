import type { ReactNode } from "react";

export type CardProps = {
  title?: ReactNode;
  eyebrow?: string;
  actions?: ReactNode;
  padded?: boolean;
  children: ReactNode;
};

export function Card({ title, eyebrow, actions, padded = false, children }: CardProps) {
  const hasHead = eyebrow !== undefined || title !== undefined || actions !== undefined;

  return (
    <section className={`card${padded ? " card--pad" : ""}`}>
      {hasHead ? (
        <div className="card__header">
          <div>
            {eyebrow ? <p className="card__eyebrow">{eyebrow}</p> : null}
            {title ? <h2 className="card__title">{title}</h2> : null}
          </div>
          {actions ? <div className="card__actions">{actions}</div> : null}
        </div>
      ) : null}
      <div className="card__body">{children}</div>
    </section>
  );
}
