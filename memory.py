import json
import os
import re
import time

FILE = "memory.json"
KINDS = ["definition", "preference", "correction", "named_filter"]
_ctx = {"dataset": ""}


def set_dataset(path):
    """Remember which dataset is loaded, so memories can be scoped to it."""
    _ctx["dataset"] = os.path.basename(path)


def _load():
    if not os.path.exists(FILE):
        return []
    try:
        with open(FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save(items):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def _words(text):
    """Lowercase words with a crude plural fix (customers -> customer)."""
    out = set()
    for w in re.findall(r"[a-z0-9]+", text.lower()):
        out.add(w[:-1] if len(w) > 3 and w.endswith("s") else w)
    return out


# ---------- tools the agent can call ----------
def save_memory(kind: str, key: str, value: str, scope: str = "this_dataset") -> dict:
    """Save a lasting fact the user told you, so it is applied in future
    sessions. Only save when the user states a definition, a correction,
    a preference, or a reusable filter. Never save ordinary questions.
    kind: definition (what a term or column means), preference (how they
    like answers, e.g. weekly summaries), correction (a fix to something
    you got wrong), or named_filter (a reusable filter like 'active customers').
    key: short name, e.g. 'active customers'.
    value: the full rule in plain words, including exact column names and
    values, e.g. 'customer_status is not cancelled'.
    scope: this_dataset (only for the loaded file) or all (every dataset).
    If the key already exists, the old value is replaced and returned."""
    if kind not in KINDS:
        return {"error": f"kind must be one of {KINDS}"}
    key = key.strip().lower()
    if not key or not value.strip():
        return {"error": "key and value cannot be empty."}
    scope_name = "all" if scope == "all" else _ctx["dataset"]
    items = _load()
    for m in items:
        if m["key"] == key and m["scope"] == scope_name:
            if m["value"].strip().lower() == value.strip().lower():
                return {"status": "already_known", "key": key}
            m.setdefault("history", []).append({"value": m["value"], "replaced_on": time.strftime("%Y-%m-%d")})
            old = m["value"]
            m["value"], m["kind"], m["updated"] = value.strip(), kind, time.strftime("%Y-%m-%d")
            _save(items)
            return {"status": "updated", "key": key, "replaced_old_value": old, "new_value": value.strip()}
    items.append({"kind": kind, "key": key, "value": value.strip(), "scope": scope_name,
                  "created": time.strftime("%Y-%m-%d"), "updated": time.strftime("%Y-%m-%d")})
    _save(items)
    return {"status": "saved", "key": key, "value": value.strip(), "scope": scope_name}


def forget_memory(key: str) -> dict:
    """Delete a saved memory when the user asks you to forget it.
    key: the name of the memory, e.g. 'active customers'."""
    key = key.strip().lower()
    items = _load()
    kept = [m for m in items if m["key"] != key]
    if len(kept) == len(items):
        return {"error": f"No memory named '{key}'.", "known_keys": [m["key"] for m in items]}
    _save(kept)
    return {"status": "forgotten", "key": key}


# ---------- retrieval (used by our code, not the agent) ----------
def relevant(question):
    """Memories that apply to this question: all preferences, plus any
    memory whose key words appear in the question. Scoped to the loaded dataset."""
    q = _words(question)
    chosen = []
    for m in _load():
        if m["scope"] not in ("all", _ctx["dataset"]):
            continue
        if m["kind"] == "preference" or (_words(m["key"]) & q):
            chosen.append(m)
    return chosen


def prompt_block(question):
    """Text added to the agent's instructions so it applies saved knowledge."""
    mems = relevant(question)
    if not mems:
        return ""
    lines = [f"- [{m['kind']}] {m['key']}: {m['value']}" for m in mems]
    return ("\n\nSAVED KNOWLEDGE FROM THE USER (apply this when answering, "
            "and mention briefly that you applied it):\n" + "\n".join(lines))


def all_memories():
    return _load()