import io
import json
import math
import mimetypes
import os
import threading

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import agent
import memory
import tools

mimetypes.add_type("application/javascript", ".js")   # Windows sometimes gets this wrong
mimetypes.add_type("text/css", ".css")

BASE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(BASE, "web")
MAX_BYTES = 25 * 1024 * 1024

tools._state["browser"] = False   # charts are sent to the page, not opened in a new tab
app = FastAPI(title="ByteVerse")
app.mount("/static", StaticFiles(directory=WEB), name="static")
_lock = threading.Lock()          # one analysis at a time (single local user)

PLOT_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#cfe9f3", family="IBM Plex Sans, Segoe UI, sans-serif"),
    colorway=["#7fdcff", "#e0b04a", "#e5484d", "#9fb3c2", "#3ea5c9"],
    margin=dict(l=55, r=20, t=60, b=55),
)


def safe(o):
    """Make any result JSON-safe (NaN and infinity become null)."""
    if o is None or isinstance(o, (bool, str, int)):
        return o
    if isinstance(o, float):
        return o if math.isfinite(o) else None
    if isinstance(o, dict):
        return {str(k): safe(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [safe(v) for v in o]
    return str(o)


def column_kind(s):
    if pd.api.types.is_bool_dtype(s):
        return "text"
    if pd.api.types.is_numeric_dtype(s):
        return "numeric"
    if pd.api.types.is_datetime64_any_dtype(s):
        return "date"
    sample = s.dropna().astype(str).head(30)
    if len(sample) and sample.str.contains(r"\d").all():
        try:
            parsed = pd.to_datetime(sample, errors="coerce")
            if parsed.notna().mean() >= 0.8:
                return "date"
        except Exception:
            pass
    return "text"


def suggestions(cols):
    nums = [c["name"] for c in cols if c["kind"] == "numeric"]
    dates = [c["name"] for c in cols if c["kind"] == "date"]
    cats = [c["name"] for c in cols if c["kind"] == "text" and 1 < c["unique"] <= 20]
    q = ["Give me an overview of this dataset."]
    if any(c["missing"] for c in cols):
        q.append("Which columns contain missing values?")
    if nums:
        q.append(f"Identify unusual values in {nums[0]}.")
    if len(nums) >= 2:
        q.append("Show me the strongest relationships between the numeric columns.")
    if dates and nums:
        q.append(f"How does {nums[0]} change over time, by month?")
    if cats and nums:
        q.append(f"Compare the average {nums[0]} across {cats[0]} and draw a chart.")
    return q[:6]


@app.get("/")
def home():
    return FileResponse(os.path.join(WEB, "index.html"))


@app.get("/api/tools")
def tool_list():
    return [{"name": f.__name__, "about": (f.__doc__ or "").strip().split("\n")[0]}
            for f in agent.TOOLS]


@app.get("/api/sample")
def get_sample(name: str):
    safe_name = os.path.basename(name)
    if safe_name not in ["sales.csv", "students.csv"]:
        raise HTTPException(404, "Sample not found")
    path = os.path.join(BASE, safe_name)
    if not os.path.exists(path):
        raise HTTPException(404, "Sample file not found")
    return FileResponse(path, filename=safe_name, media_type="text/csv")


@app.post("/api/upload")
async def upload(request: Request, filename: str):
    name = os.path.basename(filename)
    if not name.lower().endswith((".csv", ".xlsx")):
        raise HTTPException(400, "Unsupported file type. Please upload a .csv or .xlsx file.")
    data = await request.body()
    if not data:
        raise HTTPException(400, "The file is empty.")
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "The file is larger than 25 MB.")
    buf = io.BytesIO(data)
    buf.name = name
    try:
        df = tools.load_data(buf)
    except Exception as e:
        raise HTTPException(400, f"Could not read this file: {e}")
    if df.empty or df.shape[1] == 0:
        raise HTTPException(400, "The file contains no data rows.")
    memory.set_dataset(name)
    tools._state["fig"] = None

    cols = [{"name": str(c), "kind": column_kind(df[c]), "dtype": str(df[c].dtype),
             "missing": int(df[c].isna().sum()), "unique": int(df[c].nunique())}
            for c in df.columns]
    preview = json.loads(df.head(12).to_json(orient="split", date_format="iso", default_handler=str))
    return JSONResponse(safe({
        "filename": name, "bytes": len(data), "rows": int(len(df)), "columns": cols,
        "missing_cells": int(df.isna().sum().sum()), "duplicates": int(df.duplicated().sum()),
        "preview": preview, "suggestions": suggestions(cols),
    }))


class Question(BaseModel):
    question: str


@app.post("/api/ask")
def ask_question(q: Question):
    if tools._state["df"] is None:
        raise HTTPException(400, "Upload a dataset first.")
    question = q.question.strip()
    if not question:
        raise HTTPException(400, "Please type a question.")
    if len(question) > 1000:
        raise HTTPException(400, "The question is too long (max 1000 characters).")
    with _lock:
        applied = memory.relevant(question)
        tools._state["fig"] = None
        answer, trace = agent.ask(question)
        fig = tools._state["fig"]
        chart = None
        if fig is not None:
            fig.update_layout(**PLOT_LAYOUT)
            chart = json.loads(fig.to_json())
    answer = answer or "The analysis ran, but no written summary came back. See the evidence below."
    return JSONResponse(safe({"answer": answer, "trace": trace, "applied": applied, "chart": chart}))


@app.get("/api/memory")
def memory_list():
    return JSONResponse(safe(memory.all_memories()))


@app.delete("/api/memory")
def memory_forget(key: str):
    return JSONResponse(safe(memory.forget_memory(key)))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)