# ⚡ ByteVerse — AI Data Analysis Agent
> **Holographic Neural Laboratory for Autonomous Tabular Data Analytics**  
> *Powered by Google Gemini 3.1 & Deterministic Numerical Tool Execution*

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![Plotly](https://img.shields.io/badge/Plotly-Express-orange.svg)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

---

## 🌌 Overview & The Problem ByteVerse Solves

Large Language Models (LLMs) frequently hallucinate when performing numerical arithmetic, calculating percentages, or computing statistics over large tabular datasets. They cannot reliably calculate means, medians, correlation matrices, or hypothesis tests through mental arithmetic alone.

**ByteVerse** solves this problem by combining an intelligent **AI Agent (J.A.R.V.I.S.)** with a deterministic **numerical computation engine** and an immersive, futuristic holographic interface. 

Instead of guessing numbers, the AI agent interprets user intent, calls validated Python analytics tools (powered by Pandas and NumPy), verifies mathematical ground truths, and synthesizes answers with complete transparency into the execution trace.

---

## ✨ Key Features Implemented

- **Deterministic Mathematical Grounding**: Every summary statistic, filter, correlation, and outlier is calculated directly from the underlying data—zero LLM arithmetic hallucinations.
- **Full Trace Transparency**: Every tool invocation, parameter list, and intermediate result is recorded and displayed in real time.
- **Multimodal Analytical Capabilities**:
  - Dataset schema & health profiling (`profile_dataset`).
  - Single-column summary statistics: mean, median, min, max, std, quartiles (`calculate_statistics`).
  - Dynamic grouping, aggregations, and multi-condition filtering (`query_aggregate`).
  - Statistical outlier identification using the IQR rule (`detect_outliers`).
  - Automated correlation matrix calculation with constant-column exclusion (`correlation_analysis`).
  - Time-series trend analysis with linear regression slope and period comparisons (`trend_over_time`).
  - Permutation hypothesis testing (5,000 Monte Carlo shuffles) for group comparisons (`compare_groups`).
  - Automatic Plotly chart generation (bar, line, scatter, histogram) sent directly to the UI (`make_chart`).
- **Persistent Scoped Memory**: Users can define business rules, definitions, and reusable filters (e.g., *"active customers means status is not cancelled"*), which are stored in `memory.json` and automatically injected into relevant future questions (`save_memory`, `forget_memory`).
- **Futuristic Holographic Interface**: 3D Three.js neural universe with interactive telemetry rings, speech synthesis (Web Speech API), audio feedback, and dark-mode data preview tables.

---

## 🏗 Architecture & Data Flow

```mermaid
flowchart TD
    User([User Ingestion]) -->|Upload CSV/XLSX| WebUI[ByteVerse Web Interface]
    User -->|Natural Language Question| WebUI
    WebUI -->|REST API /api/ask| Server[FastAPI Server :8000]
    Server --> Agent[Agent Controller agent.py]
    Agent --> Memory[(Persistent Memory memory.json)]
    Agent -->|Structured Function Calling| Gemini[Google Gemini 3.1 Flash Lite]
    Gemini -->|Selects Analytical Tool| ToolRouter{Tool Execution}
    ToolRouter -->|Profile & Schema| ToolProfile[profile_dataset]
    ToolRouter -->|Descriptive Stats| ToolStats[calculate_statistics]
    ToolRouter -->|Group & Filter| ToolAgg[query_aggregate]
    ToolRouter -->|Outliers (IQR)| ToolOutliers[detect_outliers]
    ToolRouter -->|Pearson Correlation| ToolCorr[correlation_analysis]
    ToolRouter -->|Resample & Regression| ToolTrend[trend_over_time]
    ToolRouter -->|Permutation Test| ToolComp[compare_groups]
    ToolRouter -->|Interactive Viz| ToolViz[make_chart / Plotly]
    ToolRouter -->|Memory Retention| ToolMem[save_memory]
    ToolProfile & ToolStats & ToolAgg & ToolOutliers & ToolCorr & ToolTrend & ToolComp & ToolViz & ToolMem --> Engine[(Pandas / NumPy Engine)]
    Engine --> Agent
    Agent -->|Synthesized Grounded Answer + Trace| Server
    Server -->|JSON Response + Plotly Spec| WebUI
    WebUI -->|Render Chart & Feed Card| User
```

---

## 🛠 Technology Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic, Python-Dotenv
- **AI / LLM Orchestration**: Official Google GenAI SDK (`google-genai`), Gemini 3.1 Flash Lite (with fallback cascade to Gemini 3.8 / 3.7 / 3.5)
- **Data Analytics Engine**: Pandas, NumPy, OpenPyXL
- **Data Visualization**: Plotly Express (dark holographic theme)
- **Frontend**: Native HTML5, CSS3, JavaScript (ES6+), Three.js (3D WebGL Neural Core & Telemetry Rings)
- **Alternative UI**: Streamlit (`app.py`) for lightweight dashboarding

---

## 🚀 Installation & Local Running on Windows

### 1. Prerequisites
- **Python**: Version 3.10, 3.11, 3.12, or 3.14 installed on your system.
- **Git**: Installed and available in your terminal.

### 2. Clone the Repository
```powershell
git clone https://github.com/ankitghansyal5-crypto/ByteVerse-Ai-Agent.git
cd "ByteVerse-Ai-Agent"
```

### 3. Create and Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Configure API Credentials
ByteVerse uses Google Gemini for natural language reasoning and tool selection.
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```
Open `.env` in your editor and provide your Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```
> **Security Notice**: The `.env` file is excluded via `.gitignore`. Never commit API keys or secret credentials to version control.

---

## 🖥 How to Run the Application

### Option A: Holographic Web Application (Recommended)
Launch the primary FastAPI backend with the interactive 3D Web interface:
```powershell
python server.py
```
Open your browser and navigate to:
```
http://127.0.0.1:8000
```

### Option B: Terminal CLI Mode
To analyze datasets directly in the command prompt:
```powershell
python main.py
```

### Option C: Streamlit Interface
To run the Streamlit dashboard version:
```powershell
streamlit run app.py
```

---

## 📊 How to Upload & Ask Questions

1. Click **Initialize** on the launch screen to enter the holographic laboratory.
2. Drag and drop any **CSV** or **Excel (.xlsx)** file (or click on the sample dataset `sales.csv` / `students.csv`).
3. Once loaded, the system automatically profiles the dataset and displays column datatypes, missing cell counts, duplicate rows, and a data preview.
4. Type any question in the prompt bar:
   - *"What is the average, median, min, and max revenue?"*
   - *"What is the total revenue per region?"*
   - *"Are there any outliers in units sold?"*
   - *"What is the correlation between price and units?"*
   - *"Draw a bar chart comparing total revenue by product."*
   - *"Compare average marks across branches and tell me if the difference is statistically significant."*
   - *"Active customers means customer_status is active"* (saves rule to memory).

---

## 🧪 Testing & Verification

ByteVerse includes comprehensive unit and end-to-end integration test suites:

### Run Tool Inventory Unit Tests:
```powershell
python run_audit_tests.py
```
*Verifies all 11 individual tools across synthetic and benchmark datasets with exact assertions.*

### Run End-to-End LLM Ground-Truth Test Matrix:
```powershell
python run_e2e_tests.py
```
*Executes Tests A through J against `synthetic_test_data.csv`, validating that the LLM selects the correct tools, extracts exact ground-truth values down to decimal precision, handles edge cases, and generates Plotly charts.*

---

## 🔒 Security & Privacy

- **No Hardcoded Credentials**: API keys are strictly retrieved through environment variables or local `.env` files via `python-dotenv`.
- **Secret Scanning Compliant**: Tracked repository files contain zero credentials, passwords, or tokens.
- **Client Timeouts**: Strict 15-second HTTP deadline prevents denial-of-service hanging from upstream model outages.
- **Local Data Processing**: Tabular data is analyzed locally within your environment; only the schema and relevant aggregated tool arguments are passed to the model.

---

## ☁️ Deployment Guidelines

ByteVerse can be deployed as a containerized web service or on cloud platforms:

### Deploying to Render / Railway / Cloud Run:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**: Add `GEMINI_API_KEY` in the hosting provider's dashboard secrets.

### Live Demo URL
- **Production Status**: Local deployment active at `http://127.0.0.1:8000`. Cloud staging deployment pending user hosting configuration.

---

## 📄 License
This project is licensed under the MIT License.
