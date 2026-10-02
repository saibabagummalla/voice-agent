import os
from dotenv import load_dotenv
from groq import Groq, BadRequestError

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

Clinic hours: 10am to 6pm, Monday to Saturday, closed Sunday.
If the requested time is outside these hours, politely offer a time inside them.
If the caller asks about anything else, say you can only help with appointments."""
history = [{"role": "system", "content": SYSTEM_PROMPT}]
MODEL = "openai/gpt-oss-20b"
def ask(user_text):
    history.append({"role": "user", "content": user_text})
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=history,
            )
            break
        except BadRequestError:
            if attempt == 2:
                raise
    reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    return reply

if __name__ == "__main__":
    print("Riya: Hello, Sunrise Dental Clinic. How can I help you today?")
    while True:
        text = input("You: ")
        if text.lower() == "quit":
            break
        print("Riya:", ask(text))