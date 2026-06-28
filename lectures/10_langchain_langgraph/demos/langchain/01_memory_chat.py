"""LangChain demo: conversational chat with buffer memory."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_classic.chains import ConversationChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_openai import OpenAI

from lecture_config import require_openai_api_key

llm = OpenAI(api_key=require_openai_api_key(), temperature=0)

memory = ConversationBufferMemory(return_messages=True)

conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True,
)

print("Chat started. Type 'exit' to stop.\n")

while True:
    user_msg = input("You: ")
    if user_msg.lower() in ("exit", "quit", "q"):
        print("Bye")
        break

    reply = conversation.predict(input=user_msg)
    print("Bot:", reply)

    print("\n--- MEMORY NOW ---")
    mem_vars = memory.load_memory_variables({})
    for m in mem_vars["history"]:
        role = m.type
        print(f"{role.upper()}: {m.content}")
    print("------------------\n")
