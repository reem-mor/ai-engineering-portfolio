"""LangGraph-style demo: multi-level LLM chain decision tree for loan approval."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_classic.chains import LLMChain
from langchain_classic.prompts import PromptTemplate
from langchain_openai import OpenAI

from lecture_config import require_openai_api_key

llm = OpenAI(api_key=require_openai_api_key(), temperature=0)

approval_prompt = PromptTemplate.from_template(
    "You are a loan officer. Based on the description, classify the loan decision as 'approve' or 'reject':\n\n{input}"
)
approval_chain = LLMChain(llm=llm, prompt=approval_prompt)

risk_prompt = PromptTemplate.from_template(
    "The loan has been approved. Determine if it's 'high-risk' or 'low-risk' based on details:\n\n{input}"
)
risk_chain = LLMChain(llm=llm, prompt=risk_prompt)

reason_prompt = PromptTemplate.from_template(
    "The loan was rejected. Decide the main reason: 'income', 'credit', or 'history':\n\n{input}"
)
reason_chain = LLMChain(llm=llm, prompt=reason_prompt)

explain_risk_prompt = PromptTemplate.from_template(
    "Explain why this is considered {risk_level} risk:\n\n{input}"
)
explain_risk_chain = LLMChain(llm=llm, prompt=explain_risk_prompt)

explain_reason_prompt = PromptTemplate.from_template(
    "Explain the reasoning for rejecting due to {reason}:\n\n{input}"
)
explain_reason_chain = LLMChain(llm=llm, prompt=explain_reason_prompt)


def loan_decision_tree(query: str) -> None:
    print("INPUT QUERY:", query)
    decision = approval_chain.run(query).strip().lower()
    print(f"LEVEL 1 Decision: {decision}")

    if "approve" in decision:
        risk = risk_chain.run(query).strip().lower()
        print(f"LEVEL 2 Risk classification: {risk}")

        explanation = explain_risk_chain.run({"risk_level": risk, "input": query})
        print(f"LEVEL 3 Explanation:\n{explanation}")

    elif "reject" in decision:
        reason = reason_chain.run(query).strip().lower()
        print(f"LEVEL 2 Rejection reason: {reason}")

        explanation = explain_reason_chain.run({"reason": reason, "input": query})
        print(f"LEVEL 3 Explanation:\n{explanation}")

    else:
        print("Unknown outcome.")

    print("-" * 70)


if __name__ == "__main__":
    loan_decision_tree(
        "Customer earns $8000/month with credit score 750 and stable job."
    )
    loan_decision_tree(
        "Customer earns $2000/month with credit score 580 and past loan defaults."
    )
