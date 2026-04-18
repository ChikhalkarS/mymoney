# 💰 MyMoney – Personal Finance Tracker

A **zero-cost**, open-source personal finance web application that lets you upload bank statements, automatically categorise transactions, and visualise your spending habits with an AI-powered advisor.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📂 **CSV / Excel Upload** | Drag-and-drop or click-to-browse bank statement import |
| 🏷️ **Auto-Categorisation** | Keyword-based merchant matching: Groceries, Dining, Transport, etc. |
| 📊 **Pie / Donut Chart** | Spending breakdown by category |
| 📈 **Bar Chart** | Month-over-month spending comparison |
| 📉 **Line Graph** | Daily cash-flow time-series with average reference line |
| 🤖 **AI Advisor** | Ollama (local LLM) integration for personalised tips |
| 📋 **Rule-Based Fallback** | 50/30/20 budget rule analysis when Ollama is unavailable |
| 🧪 **Bruno API Tests** | Ready-to-run `.bru` collection for all endpoints |

---

## 🗂️ Repository Structure

```
mymoney/
├── README.md
├── frontend/                   # Next.js 14 (App Router) + Tailwind + Recharts
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── src/
│       ├── app/
│       │   ├── layout.tsx
│       │   ├── page.tsx          # Landing page
│       │   ├── globals.css
│       │   ├── upload/
│       │   │   └── page.tsx      # Upload page
│       │   └── dashboard/
│       │       ├── page.tsx      # Dashboard (SSR wrapper)
│       │       └── DashboardClient.tsx
│       └── components/
│           ├── FileUpload.tsx
│           ├── Dashboard.tsx
│           ├── SpendingPieChart.tsx
│           ├── MonthlyBarChart.tsx
│           └── DailyLineChart.tsx
├── backend/                    # FastAPI + Pandas
│   ├── requirements.txt
│   ├── main.py                 # App entry point & CORS
│   ├── uploads/                # Processed JSON files (auto-created)
│   └── app/
│       ├── categorizer.py      # Keyword → category logic
│       ├── advisor.py          # Ollama AI + 50/30/20 fallback
│       ├── models.py           # Pydantic models
│       └── routers/
│           ├── upload.py       # POST /api/upload
│           └── analysis.py     # GET /api/analysis/{file_id}
└── api-tests/                  # Bruno collection
    ├── bruno.json
    ├── health.bru
    ├── upload.bru
    ├── analysis.bru
    ├── upload_invalid.bru
    ├── analysis_not_found.bru
    └── sample_bank_statement.csv
```

---

## 🛠️ Prerequisites

| Tool | Version | Install |
|---|---|---|
| **Node.js** | ≥ 18 | [nodejs.org](https://nodejs.org) |
| **Python** | ≥ 3.11 | [python.org](https://python.org) |
| **Ollama** *(optional)* | Latest | [ollama.com](https://ollama.com) |
| **Bruno** *(optional)* | Latest | [usebruno.com](https://usebruno.com) |

---

## 🚀 Setup & Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/ChikhalkarS/mymoney.git
cd mymoney
```

---

### 2. Backend (FastAPI)

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server (default port 8000)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at **http://localhost:8000**.  
Interactive docs: **http://localhost:8000/docs**

---

### 3. Frontend (Next.js)

```bash
cd frontend

# Install dependencies
npm install

# Start the development server (default port 3000)
npm run dev
```

Open **http://localhost:3000** in your browser.

---

### 4. Ollama (Optional – AI Advisor)

If you want AI-powered financial advice instead of the rule-based fallback:

```bash
# Install Ollama (see https://ollama.com for OS-specific instructions)

# Pull a model (llama3 is used by default)
ollama pull llama3

# The Ollama service starts automatically on port 11434
# If it doesn't, run:
ollama serve
```

> **Note:** If Ollama is not running or unreachable, the app automatically falls back to the built-in 50/30/20 rule-based advisor. No configuration required.

---

## 📄 CSV / Excel Data Format

Your bank statement file must contain **at least these three columns** (column names are case-insensitive and several common aliases are accepted):

| Column | Aliases accepted | Description |
|---|---|---|
| `date` | `transaction date`, `trans date`, `posting date`, `value date` | Transaction date |
| `description` | `merchant`, `details`, `narration`, `memo`, `transaction description`, `particulars` | Merchant name or transaction description |
| `amount` | `debit`, `credit`, `transaction amount`, `value` | Transaction amount (positive = expense, negative = income/credit) |

### Example CSV

```csv
date,description,amount
2024-01-02,WALMART GROCERY,85.32
2024-01-03,NETFLIX MONTHLY,15.99
2024-01-05,AMAZON PURCHASE,49.99
2024-01-15,SALARY DIRECT DEPOSIT,-3500.00
2024-01-20,RENT PAYMENT,1200.00
```

A sample file is provided at `api-tests/sample_bank_statement.csv`.

### Supported Formats

- **CSV** (`.csv`) – comma-separated
- **Excel** (`.xlsx`, `.xls`) – standard spreadsheet

---

## 🏷️ Auto-Categorisation Rules

Transactions are categorised by matching the description against keyword lists:

| Category | Example Merchants |
|---|---|
| Groceries | Walmart, Kroger, Whole Foods, Trader Joe's, Costco |
| Dining | McDonald's, Starbucks, Chipotle, DoorDash, Uber Eats |
| Entertainment | Netflix, Spotify, Hulu, Disney+, Steam |
| Subscriptions | Generic subscription/membership keywords |
| Utilities | Electric bill, water, internet, phone (AT&T, Verizon, Comcast) |
| Housing | Rent, mortgage, property tax |
| Transportation | Uber, Lyft, gas stations, airlines |
| Healthcare | CVS, Walgreens, hospital, doctor, pharmacy |
| Shopping | Amazon, Best Buy, eBay, department stores |
| Education | Tuition, Udemy, Coursera, textbooks |
| Savings | Transfer to savings, 401k, brokerage |
| Income | Direct deposit, payroll, tax refund |
| Other | Anything not matched by the above rules |

---

## 🧪 API Testing with Bruno

1. Install [Bruno](https://usebruno.com/).
2. Open Bruno → **Open Collection** → select the `api-tests/` folder.
3. Run requests in order:
   - **Health Check** – verify the backend is up
   - **Upload Bank Statement** – upload `sample_bank_statement.csv`; the `file_id` is auto-saved
   - **Get Analysis** – retrieve charts data and advice using the saved `file_id`

---

## 📡 REST API Reference

### `GET /`
Health check.

**Response:**
```json
{ "status": "ok", "message": "MyMoney API is running." }
```

---

### `POST /api/upload`
Upload a CSV or Excel bank statement.

**Request:** `multipart/form-data` with field `file`.

**Response:**
```json
{
  "message": "File processed successfully.",
  "total_rows": 54,
  "file_id": "a1b2c3d4-..."
}
```

---

### `GET /api/analysis/{file_id}`
Retrieve spending analysis for a previously uploaded file.

**Response:**
```json
{
  "categories": [
    { "category": "Housing", "total": 3600.00, "percentage": 35.2 }
  ],
  "monthly": [
    {
      "month": "2024-01",
      "total": 1850.23,
      "categories": { "Housing": 1200.00, "Groceries": 177.42 }
    }
  ],
  "daily": [
    { "date": "2024-01-02", "total": 85.32 }
  ],
  "transactions": [
    {
      "date": "2024-01-02",
      "description": "WALMART GROCERY",
      "amount": 85.32,
      "category": "Groceries"
    }
  ],
  "advice": "💡 Rule-Based Financial Advice (50/30/20 Framework)..."
}
```

---

## 🤖 AI Advisor Details

The advisor module (`backend/app/advisor.py`) tries to call a **local Ollama instance** first:

```
POST http://localhost:11434/api/generate
{ "model": "llama3", "prompt": "...", "stream": false }
```

If Ollama is unreachable (timeout or connection error), it automatically falls back to the **rule-based 50/30/20 analyser**, which compares each spending category against recommended budget percentages and flags any overages.

To change the Ollama model, edit `OLLAMA_MODEL` in `backend/app/advisor.py`.

---

## 🔒 Privacy

All data is processed **locally on your machine**. No transaction data is sent to any external server. Ollama runs the AI model locally too — your financial data never leaves your device.

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Charts | Recharts |
| HTTP Client | Axios |
| Backend | FastAPI, Python 3.11+ |
| Data Processing | Pandas |
| Excel Support | openpyxl |
| AI Advisor | Ollama (local LLM) |
| API Testing | Bruno |

---

## 📝 License

MIT — free for personal and commercial use.