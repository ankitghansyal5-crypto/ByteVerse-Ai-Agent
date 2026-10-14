import json
import os
import sys
import pandas as pd
from starlette.testclient import TestClient

import tools
import memory
import agent
from server import app

print("=== STARTING BYTEVERSE FULL END-TO-END TEST SUITE (TESTS A - J) ===")

results = {}

# -------------------------------------------------------------
# Test A: Basic Inspection
# -------------------------------------------------------------
print("\n[RUNNING TEST A: Basic Inspection]")
tools.load_data("synthetic_test_data.csv")
memory.set_dataset("synthetic_test_data.csv")
q_a = "How many rows and columns are in this dataset, and are there any duplicate rows?"
ans_a, trace_a = agent.ask(q_a)
print("Answer A:", ans_a)
print("Trace A:", [t["tool"] for t in trace_a])
tools_called_a = [t["tool"] for t in trace_a]
assert "profile_dataset" in tools_called_a, "profile_dataset was not called in Test A"
assert "20" in ans_a, "Expected '20' rows in answer"
assert "6" in ans_a, "Expected '6' columns in answer"
assert "2" in ans_a, "Expected '2' duplicate rows in answer"
results["Test A"] = {"status": "PASS", "answer": ans_a, "tools": tools_called_a}

# -------------------------------------------------------------
# Test B: Mathematical Accuracy (Salary stats)
# -------------------------------------------------------------
print("\n[RUNNING TEST B: Mathematical Accuracy]")
q_b = "What is the average, median, minimum, and maximum salary?"
ans_b, trace_b = agent.ask(q_b)
print("Answer B:", ans_b)
print("Trace B:", [t["tool"] for t in trace_b])
tools_called_b = [t["tool"] for t in trace_b]
assert ("calculate_statistics" in tools_called_b or "profile_dataset" in tools_called_b), "calculate_statistics not called"
# Verify grounded values: mean=2025, median=2050, min=1000, max=3200
assert "2,025" in ans_b or "2025" in ans_b, "Mean 2025 not in answer"
assert "2,050" in ans_b or "2050" in ans_b, "Median 2050 not in answer"
assert "1,000" in ans_b or "1000" in ans_b, "Min 1000 not in answer"
assert "3,200" in ans_b or "3200" in ans_b, "Max 3200 not in answer"
results["Test B"] = {"status": "PASS", "answer": ans_b, "tools": tools_called_b}

# -------------------------------------------------------------
# Test C: Filtering & Aggregation (Department salaries)
# -------------------------------------------------------------
print("\n[RUNNING TEST C: Filtering and Aggregation]")
q_c = "What is the total salary for each department?"
ans_c, trace_c = agent.ask(q_c)
print("Answer C:", ans_c)
print("Trace C:", [t["tool"] for t in trace_c])
tools_called_c = [t["tool"] for t in trace_c]
assert "query_aggregate" in tools_called_c, "query_aggregate not called in Test C"
assert "21,000" in ans_c or "21000" in ans_c, "Eng 21000 not in answer"
assert "13,000" in ans_c or "13000" in ans_c, "Sales 13000 not in answer"
assert "6,500" in ans_c or "6500" in ans_c, "HR 6500 not in answer"
results["Test C"] = {"status": "PASS", "answer": ans_c, "tools": tools_called_c}

# -------------------------------------------------------------
# Test D: Data Quality & Missing Values
# -------------------------------------------------------------
print("\n[RUNNING TEST D: Data Quality and Missing Values]")
q_d = "Which columns have missing values, and how many values are missing?"
ans_d, trace_d = agent.ask(q_d)
print("Answer D:", ans_d)
print("Trace D:", [t["tool"] for t in trace_d])
tools_called_d = [t["tool"] for t in trace_d]
assert ("profile_dataset" in tools_called_d or "calculate_statistics" in tools_called_d), "profile_dataset not called"
assert "rating" in ans_d.lower(), "rating column not mentioned in missing values"
assert "4" in ans_d, "Count 4 missing not mentioned"
results["Test D"] = {"status": "PASS", "answer": ans_d, "tools": tools_called_d}

# -------------------------------------------------------------
# Test E: Correlation Analysis
# -------------------------------------------------------------
print("\n[RUNNING TEST E: Correlation Analysis]")
q_e = "What is the correlation between salary and bonus?"
ans_e, trace_e = agent.ask(q_e)
print("Answer E:", ans_e)
print("Trace E:", [t["tool"] for t in trace_e])
tools_called_e = [t["tool"] for t in trace_e]
assert "correlation_analysis" in tools_called_e, "correlation_analysis not called in Test E"
assert "1" in ans_e or "1.0" in ans_e or "perfect" in ans_e.lower(), "Correlation 1.0 not identified"
results["Test E"] = {"status": "PASS", "answer": ans_e, "tools": tools_called_e}

# -------------------------------------------------------------
# Test F: Multi-Tool Reasoning / Compare Groups
# -------------------------------------------------------------
print("\n[RUNNING TEST F: Multi-Tool Reasoning]")
q_f = "Compare the average salary across departments, and is the difference statistically significant?"
ans_f, trace_f = agent.ask(q_f)
print("Answer F:", ans_f)
print("Trace F:", [t["tool"] for t in trace_f])
tools_called_f = [t["tool"] for t in trace_f]
assert ("compare_groups" in tools_called_f or "query_aggregate" in tools_called_f), "compare tool not called"
results["Test F"] = {"status": "PASS", "answer": ans_f, "tools": tools_called_f}

# -------------------------------------------------------------
# Test G: Dynamic Dataset Support (students.csv)
# -------------------------------------------------------------
print("\n[RUNNING TEST G: Dynamic Dataset Support]")
tools.load_data("students.csv")
memory.set_dataset("students.csv")
q_g = "What is the average marks in this dataset?"
ans_g, trace_g = agent.ask(q_g)
print("Answer G:", ans_g)
print("Trace G:", [t["tool"] for t in trace_g])
tools_called_g = [t["tool"] for t in trace_g]
# Ground truth for students.csv marks mean:
stu_df = pd.read_csv("students.csv")
marks_mean = round(stu_df["marks"].mean(), 2)
print("Actual ground truth marks mean:", marks_mean)
assert str(int(marks_mean)) in ans_g or f"{marks_mean:.1f}" in ans_g or f"{marks_mean:.2f}" in ans_g
results["Test G"] = {"status": "PASS", "answer": ans_g, "tools": tools_called_g}

# -------------------------------------------------------------
# Test H: API Error Handling Simulation
# -------------------------------------------------------------
print("\n[RUNNING TEST H: API Error Handling]")
err_401 = agent._friendly_error(Exception("401 Unauthorized: API_KEY_INVALID"))
assert "Invalid or unauthorized API key" in err_401
err_429 = agent._friendly_error(Exception("429 RESOURCE_EXHAUSTED: rate limit exceeded"))
assert "rate limit or quota exceeded" in err_429
err_503 = agent._friendly_error(Exception("503 UNAVAILABLE: high demand"))
assert "high demand" in err_503
err_timeout = agent._friendly_error(Exception("504 DEADLINE_EXCEEDED: timeout"))
assert "timed out after 15 seconds" in err_timeout
print("Error handling simulations verified:", [err_401, err_429, err_503, err_timeout])
results["Test H"] = {"status": "PASS", "details": "All error status codes mapped to actionable user messages"}

# -------------------------------------------------------------
# Test I: Invalid Inputs & Boundary Cases
# -------------------------------------------------------------
print("\n[RUNNING TEST I: Invalid Inputs]")
bad_col = tools.calculate_statistics("non_existent_column")
assert "error" in bad_col and "does not exist" in bad_col["error"]

bad_metric = tools.query_aggregate(group_by="branch", metric="branch", agg="sum")
assert "error" in bad_metric and "must be numeric" in bad_metric["error"]

bad_op = tools.query_aggregate(group_by="branch", metric="marks", filter_column="marks", filter_op="LIKE", filter_value="50")
assert "error" in bad_op and "Unknown filter_op" in bad_op["error"]
print("Invalid inputs caught cleanly:", [bad_col["error"], bad_metric["error"], bad_op["error"]])
results["Test I"] = {"status": "PASS", "details": "Robust input validation and descriptive error responses"}

# -------------------------------------------------------------
# Test J: Frontend / HTTP Endpoint Integration
# -------------------------------------------------------------
print("\n[RUNNING TEST J: Frontend / HTTP Endpoint Integration]")
client = TestClient(app)

# 1. Test /api/tools
res_tools = client.get("/api/tools")
assert res_tools.status_code == 200
tool_names = [t["name"] for t in res_tools.json()]
print("Registered API tools:", tool_names)
assert "calculate_statistics" in tool_names
assert "profile_dataset" in tool_names

# 2. Test /api/upload
with open("synthetic_test_data.csv", "rb") as f:
    upload_res = client.post("/api/upload?filename=synthetic_test_data.csv", content=f.read())
assert upload_res.status_code == 200
up_json = upload_res.json()
assert up_json["rows"] == 20
assert up_json["duplicates"] == 2
assert up_json["missing_cells"] == 4
print("Upload endpoint verified:", up_json["filename"], up_json["rows"], "rows")

# 3. Test /api/ask with chart generation
ask_res = client.post("/api/ask", json={"question": "Draw a bar chart comparing total salary by department."})
assert ask_res.status_code == 200
ask_json = ask_res.json()
print("Ask JSON keys:", list(ask_json.keys()))
assert "answer" in ask_json
assert "trace" in ask_json
assert "chart" in ask_json
assert ask_json["chart"] is not None, "Plotly chart was not generated!"
assert "data" in ask_json["chart"] and "layout" in ask_json["chart"]
print("Chart generated successfully:", ask_json["chart"]["data"][0]["type"])
results["Test J"] = {"status": "PASS", "details": "Full HTTP stack with upload, ask, trace, and Plotly chart"}

print("\n=======================================================")
print("=== ALL TESTS (A THROUGH J) SUCCESSFULLY PASSED! ===")
print("=======================================================")

with open("test_results_summary.json", "w") as f:
    json.dump(results, f, indent=2)
print("Saved summary to test_results_summary.json")
