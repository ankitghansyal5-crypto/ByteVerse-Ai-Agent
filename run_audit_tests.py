import os
import sys
import json
import pandas as pd
import numpy as np

import tools
import memory
import agent

print("=== STARTING BYTEVERSE TOOL & AGENT AUDIT ===")

# 1. LOAD TEST DATASET
df = tools.load_data("synthetic_test_data.csv")
memory.set_dataset("synthetic_test_data.csv")
print(f"Loaded synthetic_test_data.csv: {df.shape[0]} rows, {df.shape[1]} cols")

# 2. AUDIT TOOL INVENTORY
tool_results = {}

# Tool 1: profile_dataset
t1 = tools.profile_dataset()
assert t1["rows"] == 20, f"Expected 20 rows, got {t1['rows']}"
assert t1["duplicate_rows"] == 2, f"Expected 2 dups, got {t1['duplicate_rows']}"
assert len(t1["columns"]) == 6, f"Expected 6 cols, got {len(t1['columns'])}"
tool_results["profile_dataset"] = "PASS"

# Tool 2: calculate_statistics
t2_sal = tools.calculate_statistics("salary")
assert t2_sal["count"] == 20
assert t2_sal["min"] == 1000.0
assert t2_sal["max"] == 3200.0
assert t2_sal["mean"] == 2025.0
assert t2_sal["median"] == 2050.0
assert t2_sal["sum"] == 40500.0
tool_results["calculate_statistics"] = "PASS"

# Tool 3: query_aggregate
t3_sum = tools.query_aggregate(group_by="department", metric="salary", agg="sum")
assert t3_sum["result"]["Eng"] == 21000.0
assert t3_sum["result"]["Sales"] == 13000.0
assert t3_sum["result"]["HR"] == 6500.0

t3_filtered = tools.query_aggregate(group_by="department", metric="salary", agg="count",
                                    filter_column="salary", filter_op=">", filter_value="2000")
print("t3_filtered result:", t3_filtered["result"])
assert t3_filtered["result"]["Eng"] == 5
assert t3_filtered["result"]["Sales"] == 5
tool_results["query_aggregate"] = "PASS"

# Tool 4: detect_outliers
t4 = tools.detect_outliers("salary")
assert "normal_range" in t4
assert "outlier_count" in t4
tool_results["detect_outliers"] = "PASS"

# Tool 5: correlation_analysis
t5 = tools.correlation_analysis()
assert "strongest_pairs" in t5
assert "constant_columns_excluded" in t5
assert "fixed_allowance" in t5["constant_columns_excluded"]
# salary and bonus are perfectly correlated (bonus = salary / 10)
top_pair = t5["strongest_pairs"][0]
assert (top_pair["column_a"] in ["salary", "bonus"] and top_pair["column_b"] in ["salary", "bonus"])
assert top_pair["correlation"] == 1.0
tool_results["correlation_analysis"] = "PASS"

# Tool 6: compare_groups
t6 = tools.compare_groups("department", "salary")
assert "group_averages" in t6
assert "p_value" in t6
assert t6["group_averages"]["Eng"] == 2333.33
assert t6["group_averages"]["Sales"] == 2166.67
assert t6["group_averages"]["HR"] == 1300.0
tool_results["compare_groups"] = "PASS"

# Tool 7: make_chart
tools._state["browser"] = False
t7 = tools.make_chart("bar", x="department", y="salary", agg="mean", title="Mean Salary by Dept")
assert os.path.exists(t7["saved_to"])
tool_results["make_chart"] = "PASS"

# Tool 8 & 9: memory save & forget
mem_save = memory.save_memory("definition", "seniority", "salary greater than 2500")
assert mem_save["status"] in ["saved", "already_known"]
mem_forget = memory.forget_memory("seniority")
assert mem_forget["status"] == "forgotten"
tool_results["memory_tools"] = "PASS"

# Tool 10: trend_over_time (test with sales.csv)
tools.load_data("sales.csv")
# Test bad column handling
t_bad = tools.trend_over_time(date_column="order_date", metric="revenue", period="month")
assert "error" in t_bad

# Test real trend
t10 = tools.trend_over_time(date_column="date", metric="revenue", period="month")
print("t10 result:", t10)
assert "direction" in t10
assert "series" in t10
tool_results["trend_over_time"] = "PASS"

# Reload synthetic test data
tools.load_data("synthetic_test_data.csv")
memory.set_dataset("synthetic_test_data.csv")

print("\n--- ALL INDIVIDUAL TOOL TESTS PASSED ---")
for k, v in tool_results.items():
    print(f"  {k}: {v}")
