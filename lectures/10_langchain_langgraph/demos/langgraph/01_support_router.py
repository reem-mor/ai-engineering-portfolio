"""LangGraph demo: support router with conditional edges."""

import sys
from pathlib import Path
from typing import TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from lecture_config import require_openai_api_key

llm = ChatOpenAI(api_key=require_openai_api_key(), temperature=0)


class SupportState(TypedDict, total=False):
    message: str
    intent: str
    response: str


def classify_intent(state: SupportState) -> SupportState:
    msg = state["message"].lower()
    if any(x in msg for x in ["error", "bug", "site", "login", "crash"]):
        intent = "technical"
    elif any(x in msg for x in ["refund", "invoice", "payment", "charged"]):
        intent = "billing"
    elif any(x in msg for x in ["lesson", "exercise", "explain", "understand"]):
        intent = "content"
    else:
        intent = "unknown"

    print(f"Intent classified as: {intent}")
    return {"intent": intent}


def handle_technical(state: SupportState) -> SupportState:
    message = state["message"]
    prompt = f"""
    You are a technical support agent.
    The user said: {message}
    Provide clear steps to fix it.
    """
    resp = llm.invoke(prompt)
    return {"response": resp.content}


def handle_billing(state: SupportState) -> SupportState:
    message = state["message"]
    prompt = f"""
    You are a billing assistant.
    The user said: {message}
    Explain politely how billing/refunds work and who to contact.
    """
    resp = llm.invoke(prompt)
    return {"response": resp.content}


def handle_content(state: SupportState) -> SupportState:
    message = state["message"]
    prompt = f"""
    You are a course tutor.
    The user said: {message}
    Give a short, friendly explanation to help them learn.
    """
    resp = llm.invoke(prompt)
    return {"response": resp.content}


def handle_unknown(state: SupportState) -> SupportState:
    message = state["message"]
    prompt = f"""
    You are a virtual assistant.
    The user said: {message}
    You are not sure what category this is.
    Ask them for clarification.
    """
    resp = llm.invoke(prompt)
    return {"response": resp.content}


graph = StateGraph(SupportState)

graph.add_node("classify", classify_intent)
graph.add_node("technical", handle_technical)
graph.add_node("billing", handle_billing)
graph.add_node("content", handle_content)
graph.add_node("unknown", handle_unknown)

graph.set_entry_point("classify")


def route(state: SupportState) -> str:
    return state["intent"]


graph.add_conditional_edges(
    "classify",
    route,
    {
        "technical": "technical",
        "billing": "billing",
        "content": "content",
        "unknown": "unknown",
    },
)

for node in ["technical", "billing", "content", "unknown"]:
    graph.add_edge(node, END)

app = graph.compile()


if __name__ == "__main__":
    examples = [
        "I keep getting a login error on the website.",
        "I was double charged for the Python course.",
        "I don't understand how RAG works in the AI lesson.",
        "Hello, I just want to say thanks!",
    ]

    for msg in examples:
        print("\nNEW MESSAGE:", msg)
        result = app.invoke({"message": msg})
        print("Final Response:", result["response"])
