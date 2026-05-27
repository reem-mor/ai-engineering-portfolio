export type ExampleQuestionChipsProps = {
  label: string;
  questions: readonly string[];
  onSelect: (question: string) => void;
  disabled?: boolean;
};

export function ExampleQuestionChips({ label, questions, onSelect, disabled }: ExampleQuestionChipsProps) {
  return (
    <div className="example-chips">
      <p className="example-chips__label" id="example-chips-label">
        {label}
      </p>
      <div className="example-chips__row" role="group" aria-labelledby="example-chips-label">
        {questions.map((q) => (
          <button
            key={q}
            type="button"
            className="example-chips__btn"
            disabled={disabled}
            onClick={() => onSelect(q)}
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
