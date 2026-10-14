import tools
import memory
from agent import ask

path = input("Which CSV file? (e.g. sales.csv): ")
tools.load_data(path)
memory.set_dataset(path)
print("Loaded! Ask questions. Commands: /memory (see what I remember), /forget name, quit\n")

while True:
    question = input("You: ").strip()
    if question.lower() == "quit":
        break
    if question == "/memory":
        mems = memory.all_memories()
        if not mems:
            print("Nothing remembered yet.\n")
        for m in mems:
            print(f"- [{m['kind']}] {m['key']}: {m['value']}  (scope: {m['scope']})")
        print()
        continue
    if question.startswith("/forget "):
        print(memory.forget_memory(question[8:]), "\n")
        continue

    applied = memory.relevant(question)
    answer, trace = ask(question)

    if applied:
        print("\n--- MEMORY APPLIED ---")
        for m in applied:
            print(f"{m['key']}: {m['value']}")
    print("\n--- TOOLS THE AGENT USED ---")
    for step in trace:
        print(step["tool"], step["inputs"])
    print("\nAGENT:", answer, "\n")