export type EmptyStatePanelProps = {
  title: string;
  description: string;
  steps?: readonly string[];
};

export function EmptyStatePanel({ title, description, steps }: EmptyStatePanelProps) {
  return (
    <section className="empty-state" aria-label={title}>
      <p className="empty-state__kicker">Awaiting query</p>
      <h2 className="empty-state__title">{title}</h2>
      <p className="empty-state__desc">{description}</p>
      {steps && steps.length > 0 ? (
        <ol className="empty-state__steps">
          {steps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      ) : null}
    </section>
  );
}
