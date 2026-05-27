import { KB_PIPELINE_STEPS } from "../../content/opsCopy";

export function PipelineSteps() {
  return (
    <ol className="pipeline-steps" aria-label="Knowledge base indexing flow">
      {KB_PIPELINE_STEPS.map((item, index) => (
        <li key={item.step} className="pipeline-steps__item">
          <span className="pipeline-steps__num" aria-hidden>
            {item.step}
          </span>
          <div className="pipeline-steps__body">
            <span className="pipeline-steps__label">{item.label}</span>
            <span className="pipeline-steps__detail">{item.detail}</span>
          </div>
          {index < KB_PIPELINE_STEPS.length - 1 ? (
            <span className="pipeline-steps__connector" aria-hidden />
          ) : null}
        </li>
      ))}
    </ol>
  );
}
