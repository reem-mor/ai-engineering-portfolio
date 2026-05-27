import type { QuestionGroup } from "../../content/opsCopy";

export type GroupedExampleQuestionsProps = {
  groups: readonly QuestionGroup[];
  onSelect: (question: string) => void;
  disabled?: boolean;
};

export function GroupedExampleQuestions({ groups, onSelect, disabled }: GroupedExampleQuestionsProps) {
  return (
    <div className="example-chips example-chips--grouped">
      <p className="example-chips__heading">Example questions by topic</p>
      {groups.map((group) => (
        <div key={group.id} className="example-chips__group">
          <p className="example-chips__label">{group.label}</p>
          <div className="example-chips__row" role="group" aria-label={`${group.label} examples`}>
            {group.questions.map((q) => (
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
      ))}
    </div>
  );
}
