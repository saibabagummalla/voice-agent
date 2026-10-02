import os
from dotenv import load_dotenv
from groq import Groq, BadRequestError
import json
from tools import TOOLS, FUNCTIONS, init_db

init_db()
load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])

SYSTEM_PROMPT = """You are Riya, a phone receptionist for Sunrise Dental Clinic.

Speaking rules:
- Maximum two short sentences per reply.
- No lists, markdown, or emojis. Your words are spoken aloud.
- Ask only ONE question per reply. Never answer on behalf of the caller.

Your only job is to book an appointment. You need exactly three details:
1. Full name (first and last)
2. Preferred date
3. Preferred time

Process:
- Ask for the missing details one at a time, in the order above.
- Never assume or invent a detail the caller has not said.
- Do not say the appointment is booked until you have all three details.
- When you have all three, read them back and ask "Shall I confirm that?"
- After the caller says yes, say the appointment is confirmed and say goodbye.
."""
history = [{"role": "system", "content": SYSTEM_PROMPT}]
MODEL = "openai/gpt-oss-20b"
def ask(user_text):
    history.append({"role": "user", "content": user_text})
    for _ in range(5):  # safety limit on tool rounds
        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model=MODEL, messages=history,
                    tools=TOOLS, tool_choice="auto")
                break
            except BadRequestError:
                if attempt == 2:
                    raise
        msg = response.choices[0].message

        if not msg.tool_calls:
            history.append({"role": "assistant", "content": msg.content})
            return msg.content

        history.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [{"id": tc.id, "type": "function",
                            "function": {"name": tc.function.name,
                                         "arguments": tc.function.arguments}}
                           for tc in msg.tool_calls]})

        for tc in msg.tool_calls:
            fn = FUNCTIONS.get(tc.function.name)
            try:
                result = fn(**json.loads(tc.function.arguments)) if fn else {"error": "unknown tool"}
            except Exception as e:
                result = {"error": str(e)}
            print(f"  [tool] {tc.function.name} -> {result}")
            history.append({"role": "tool", "tool_call_id": tc.id,
                            "content": json.dumps(result)})
    return "Sorry, something went wrong. Could you say that again?"

if __name__ == "__main__":
    print("Riya: Hello, Sunrise Dental Clinic. How can I help you today?")
    while True:
        text = input("You: ")
        if text.lower() == "quit":
            break
        print("Riya:", ask(text))