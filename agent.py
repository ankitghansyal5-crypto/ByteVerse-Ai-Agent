import functools
import time
from google import genai
from google.genai import types
from api_key import GEMINI_API_KEY
import tools
import memory

MODEL = "gemini-3.1-flash-lite"
MODELS = [
    MODEL,
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-flash-lite-latest",
    "gemini-flash-latest",
]

client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(timeout=15000)
)

trace = []   # a log of every tool the agent uses


def traced(fn):
    """Wraps a tool so every call gets recorded in the trace."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        trace.append({"tool": fn.__name__, "inputs": kwargs, "result": result})
        return result
    return wrapper


TOOLS = [traced(f) for f in [
    tools.profile_dataset,
    tools.calculate_statistics,
    tools.query_aggregate,
    tools.detect_outliers,
    tools.correlation_analysis,
    tools.trend_over_time,
    tools.compare_groups,
    tools.make_chart,
    memory.save_memory,
    memory.forget_memory,
]]

SYSTEM_PROMPT = """You are a careful data analyst working on a table the user loaded.
Rules:
1. Never guess numbers. Always use your tools to get facts from the data.
2. If you don't know the columns, call profile_dataset first.
3. For summary statistics (average/mean, median, min, max, standard deviation), call calculate_statistics.
4. For group summaries, filtering, or aggregations, call query_aggregate.
5. If a tool returns an error, read it, fix your input, and try again.
6. In your answer, give the real numbers and say briefly how you got them.
7. If you had to assume something (e.g. which column means revenue), say so.

Memory rules:
8. If the user states a definition, correction, preference or reusable filter
   (for example "active customers means status is not cancelled"), call
   save_memory. Do NOT save ordinary questions or one-off requests.
9. If SAVED KNOWLEDGE is listed below, apply it to your analysis (translate
   definitions into tool filters) and mention briefly that you applied it.
10. If save_memory says it replaced an old value, tell the user what changed.
11. If the user asks you to forget something, call forget_memory."""


def _friendly_error(err):
    msg = str(err)
    err_type = type(err).__name__
    if "401" in msg or "403" in msg or "API_KEY_INVALID" in msg:
        return "Invalid or unauthorized API key. Please check your GEMINI_API_KEY configuration."
    if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
        return "Google Gemini API rate limit or quota exceeded. Please wait a moment and try again."
    if "503" in msg or "UNAVAILABLE" in msg:
        return "The AI model is temporarily experiencing high demand (503). Please retry in a few moments."
    if "504" in msg or "DEADLINE_EXCEEDED" in msg or "timeout" in msg.lower():
        return "Request timed out after 15 seconds. The AI service did not respond in time."
    if "404" in msg or "NOT_FOUND" in msg:
        return f"Configured AI model was not accessible ({err_type})."
    return f"AI service error ({err_type}): {msg[:180]}"


def ask(question):
    trace.clear()
    instructions = SYSTEM_PROMPT + memory.prompt_block(question)
    last_error = None
    for model in MODELS:
        attempts = 2 if model == MODEL else 1
        for attempt in range(attempts):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=question,
                    config=types.GenerateContentConfig(
                        system_instruction=instructions,
                        tools=TOOLS,
                        temperature=0.1,
                    ),
                )
                text = response.text or ""
                return text, list(trace)
            except Exception as e:
                last_error = e
                trace.clear()
                time.sleep(1)
    return _friendly_error(last_error), []