import json
import os
import webbrowser
import pandas as pd
import numpy as np
import plotly.express as px

# ---------- the dataset currently loaded ----------
_state = {"df": None, "fig": None, "browser": True}


def load_data(source):
    """Load a CSV or Excel file (a path or an uploaded file) so the tools can analyse it."""
    name = getattr(source, "name", str(source)).lower()
    if name.endswith(".xlsx"):
        _state["df"] = pd.read_excel(source)
    else:
        _state["df"] = pd.read_csv(source)
    return _state["df"]


def _df():
    if _state["df"] is None:
        raise ValueError("No dataset loaded yet.")
    return _state["df"]


def _clean(obj):
    """Turn numpy/pandas values into plain Python so they can be sent to the AI."""
    return json.loads(json.dumps(obj, default=lambda o: o.item() if hasattr(o, "item") else str(o)))


def _bad_column(col):
    return {"error": f"Column '{col}' does not exist.",
            "available_columns": list(_df().columns)}


# ---------- TOOL 1: profile ----------
def profile_dataset() -> dict:
    """Describe the whole dataset: number of rows, each column's type,
    missing values, number of unique values and example values.
    Use this first when you don't know what the data looks like."""
    df = _df()
    columns = []
    for c in df.columns:
        columns.append({
            "name": c,
            "type": str(df[c].dtype),
            "missing": int(df[c].isna().sum()),
            "unique_values": int(df[c].nunique()),
            "examples": df[c].dropna().unique()[:4].tolist(),
        })
    return _clean({"rows": len(df), "duplicate_rows": int(df.duplicated().sum()),
                   "columns": columns})


# ---------- TOOL 2: calculate statistics ----------
def calculate_statistics(column: str) -> dict:
    """Calculate descriptive statistics for a numeric column: count, mean (average),
    median, std (standard deviation), min, max, sum, and quartiles (25th and 75th percentiles).
    Use this when asked for summary statistics, average, median, minimum, maximum, or standard deviation."""
    df = _df()
    if column not in df.columns:
        return _bad_column(column)
    if not pd.api.types.is_numeric_dtype(df[column]):
        return {"error": f"Column '{column}' is not numeric.",
                "column_type": str(df[column].dtype)}
    s = pd.to_numeric(df[column], errors="coerce").dropna()
    if s.empty:
        return {"error": f"Column '{column}' contains no non-null numeric values."}
    return _clean({
        "column": column,
        "count": int(s.count()),
        "missing": int(df[column].isna().sum()),
        "sum": round(float(s.sum()), 2),
        "mean": round(float(s.mean()), 2),
        "median": round(float(s.median()), 2),
        "std": round(float(s.std()), 2) if len(s) > 1 else 0.0,
        "min": round(float(s.min()), 2),
        "max": round(float(s.max()), 2),
        "q25": round(float(s.quantile(0.25)), 2),
        "q75": round(float(s.quantile(0.75)), 2),
    })


# ---------- TOOL 3: group and aggregate ----------
def query_aggregate(group_by: str, metric: str, agg: str = "sum",
                    top_n: int = 10, filter_column: str = "",
                    filter_value: str = "", filter_op: str = "==") -> dict:
    """Group rows by one column and calculate a number for each group.
    group_by: column to split by (e.g. region).
    metric: numeric column to calculate (e.g. revenue).
    agg: one of sum, mean, median, count, min, max.
    top_n: how many groups to return, highest first.
    filter_column, filter_value, filter_op (all optional): keep only rows
    that pass the filter before grouping. filter_op is one of
    ==, !=, >, <, >=, <= (default ==). Use != to exclude a value,
    for example filter_column=customer_status, filter_op=!=, filter_value=cancelled."""
    df = _df()
    for col in (group_by, metric):
        if col not in df.columns:
            return _bad_column(col)
    if agg not in ["sum", "mean", "median", "count", "min", "max"]:
        return {"error": f"Unknown agg '{agg}'.",
                "allowed": ["sum", "mean", "median", "count", "min", "max"]}
    if agg != "count" and not pd.api.types.is_numeric_dtype(df[metric]):
        return {"error": f"Metric column '{metric}' must be numeric for aggregation '{agg}'."}
    if filter_column:
        if filter_column not in df.columns:
            return _bad_column(filter_column)
        if filter_op not in ["==", "!=", ">", "<", ">=", "<="]:
            return {"error": f"Unknown filter_op '{filter_op}'.",
                    "allowed": ["==", "!=", ">", "<", ">=", "<="]}
        if filter_op in ("==", "!="):
            match = df[filter_column].astype(str) == str(filter_value)
            df = df[match] if filter_op == "==" else df[~match]
        else:
            try:
                val = float(filter_value)
            except ValueError:
                return {"error": "For >, <, >=, <= the filter_value must be a number."}
            col = pd.to_numeric(df[filter_column], errors="coerce")
            df = df[{">": col > val, "<": col < val, ">=": col >= val, "<=": col <= val}[filter_op]]
    if len(df) == 0:
        return _clean({"rows_used": 0, "result": {}, "note": "No rows matched the filter criteria."})
    result = df.groupby(group_by)[metric].agg(agg).sort_values(ascending=False)
    return _clean({"rows_used": len(df), "result": result.head(top_n).round(2).to_dict()})


# ---------- TOOL 4: outliers ----------
def detect_outliers(column: str) -> dict:
    """Find unusually high or low values in a numeric column using the
    IQR rule (values far outside the middle 50% of the data).
    Returns how many outliers exist and the most extreme rows."""
    df = _df()
    if column not in df.columns:
        return _bad_column(column)
    if not pd.api.types.is_numeric_dtype(df[column]):
        return {"error": f"'{column}' is not numeric."}
    s = pd.to_numeric(df[column], errors="coerce").dropna()
    if s.empty:
        return {"error": f"Column '{column}' contains no numeric values."}
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    out = df[(df[column] < low) | (df[column] > high)]
    worst = out.reindex(out[column].sub(s.median()).abs()
                        .sort_values(ascending=False).index).head(5)
    return _clean({"column": column, "normal_range": [round(low, 2), round(high, 2)],
                   "outlier_count": len(out),
                   "most_extreme_rows": worst.to_dict("records")})


# ---------- TOOL 5: correlations ----------
def correlation_analysis() -> dict:
    """Find which numeric columns move together. Returns the strongest
    pairs with a correlation between -1 and 1 (close to 1 = rise together,
    close to -1 = one rises as the other falls, near 0 = unrelated)."""
    num = _df().select_dtypes(include="number")
    constant_cols = [c for c in num.columns if num[c].dropna().nunique() <= 1]
    valid_num = num[[c for c in num.columns if c not in constant_cols]]
    if valid_num.shape[1] < 2:
        return {
            "error": "Need at least two non-constant numeric columns to compute correlations.",
            "constant_columns": constant_cols
        }
    corr = valid_num.corr()
    pairs = []
    cols = list(corr.columns)
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            val = corr.iloc[i, j]
            if pd.notna(val):
                pairs.append({
                    "column_a": cols[i],
                    "column_b": cols[j],
                    "correlation": round(float(val), 3)
                })
    pairs.sort(key=lambda p: abs(p["correlation"]), reverse=True)
    res = {"strongest_pairs": pairs[:6]}
    if constant_cols:
        res["constant_columns_excluded"] = constant_cols
    return _clean(res)


# ---------- TOOL 6: trend over time ----------
def trend_over_time(date_column: str, metric: str, period: str = "month",
                    agg: str = "sum") -> dict:
    """Show how a numeric column changes over time and whether it is
    going up or down overall.
    date_column: the column holding dates.
    metric: numeric column to track (e.g. revenue).
    period: day, week or month.
    agg: sum, mean or count."""
    df = _df()
    for col in (date_column, metric):
        if col not in df.columns:
            return _bad_column(col)
    freq = {"day": "D", "week": "W", "month": "MS"}.get(period)
    if freq is None:
        return {"error": "period must be day, week or month"}
    if agg not in ["sum", "mean", "count"]:
        return {"error": "agg must be sum, mean or count"}
    d = df[[date_column, metric]].copy()
    d[date_column] = pd.to_datetime(d[date_column], errors="coerce")
    d[metric] = pd.to_numeric(d[metric], errors="coerce")
    d = d.dropna()
    if d.empty:
        return {"error": f"'{date_column}' or '{metric}' has no valid rows."}
    series = d.set_index(date_column)[metric].resample(freq).agg(agg).dropna()
    if series.empty:
        return {"error": f"No valid periods found in '{date_column}'."}
    values = series.values.astype(float)
    slope = float(np.polyfit(range(len(values)), values, 1)[0]) if len(values) > 1 else 0.0
    half = len(values) // 2
    first = values[:half].mean() if half > 0 else 0.0
    second = values[half:].mean() if half > 0 else 0.0
    change = round((second - first) / first * 100, 1) if (half > 0 and first != 0) else None
    return _clean({
        "period": period,
        "number_of_periods": len(values),
        "direction": "up" if slope > 0 else ("down" if slope < 0 else "flat"),
        "second_half_vs_first_half_percent": change,
        "best_period": {"date": str(series.idxmax().date()), "value": round(float(series.max()), 2)},
        "worst_period": {"date": str(series.idxmin().date()), "value": round(float(series.min()), 2)},
        "series": {str(k.date()): round(float(v), 2) for k, v in series.head(24).items()},
    })


# ---------- TOOL 6: compare groups (permutation test, no scipy needed) ----------
def _f_stat(values, codes, k):
    """How much the group averages differ, relative to the spread inside groups."""
    n = len(values)
    grand = values.mean()
    counts = np.bincount(codes, minlength=k)
    means = np.bincount(codes, weights=values, minlength=k) / counts
    between = (counts * (means - grand) ** 2).sum() / (k - 1)
    squares = np.bincount(codes, weights=values ** 2, minlength=k)
    within = (squares - counts * means ** 2).sum() / (n - k)
    return between / within if within > 0 else 0.0


def compare_groups(group_column: str, metric: str) -> dict:
    """Test whether a numeric column is really different between groups
    (e.g. is average marks different across branches?). Returns each
    group's average and a p-value from a permutation test: below 0.05
    means the difference is statistically significant, above 0.05 means
    it could easily be chance."""
    df = _df()
    for col in (group_column, metric):
        if col not in df.columns:
            return _bad_column(col)
    if not pd.api.types.is_numeric_dtype(df[metric]):
        return {"error": f"'{metric}' is not numeric."}
    d = df[[group_column, metric]].dropna()
    sizes = d.groupby(group_column)[metric].transform("size")
    d = d[sizes >= 2]
    codes, labels = pd.factorize(d[group_column])
    k = len(labels)
    if k < 2:
        return {"error": "Need at least two groups with 2+ rows each."}
    values = d[metric].to_numpy(dtype=float)
    observed = _f_stat(values, codes, k)
    rng = np.random.default_rng(0)
    shuffled = codes.copy()
    hits = 0
    runs = 5000
    for _ in range(runs):
        rng.shuffle(shuffled)
        if _f_stat(values, shuffled, k) >= observed:
            hits += 1
    p = (hits + 1) / (runs + 1)
    averages = d.groupby(group_column)[metric].mean().round(2).to_dict()
    return _clean({
        "test": "permutation test on group differences (5000 shuffles)",
        "group_averages": averages,
        "p_value": round(p, 4),
        "significant_at_5_percent": bool(p < 0.05),
    })


# ---------- TOOL 7: chart ----------
def make_chart(chart_type: str, x: str, y: str = "", agg: str = "sum",
               title: str = "") -> dict:
    """Draw a chart.
    chart_type: bar, line, scatter or histogram.
    x: column for the horizontal axis.
    y: numeric column for the vertical axis (not needed for histogram).
    agg: for bar and line charts, how to combine rows per x value (sum, mean, count)."""
    df = _df()
    for col in (x, y):
        if col and col not in df.columns:
            return _bad_column(col)
    if chart_type in ("bar", "line"):
        if not y:
            return {"error": "bar and line charts need a y column."}
        data = df.groupby(x)[y].agg(agg).reset_index()
        fig = (px.bar if chart_type == "bar" else px.line)(data, x=x, y=y, title=title)
    elif chart_type == "scatter":
        if not y:
            return {"error": "scatter charts need a y column."}
        fig = px.scatter(df, x=x, y=y, title=title)
    elif chart_type == "histogram":
        fig = px.histogram(df, x=x, title=title)
    else:
        return {"error": "chart_type must be bar, line, scatter or histogram."}
    _state["fig"] = fig   # the app displays this inside the chat
    os.makedirs("charts", exist_ok=True)
    path = os.path.abspath(os.path.join("charts", f"{chart_type}_{x}_{y}.html"))
    fig.write_html(path)
    if _state["browser"]:   # only the terminal version opens a browser tab
        webbrowser.open("file://" + path)
    return {"saved_to": path, "chart_type": chart_type}