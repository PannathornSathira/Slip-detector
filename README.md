# Payment Slip OCR & Finance Tracker

An intelligent, self-learning finance tracking application that extracts transaction data from Thai bank payment slips using OCR and automatically categorizes them. It provides a visual dashboard for financial analysis and a label manager interface to easily train and update merchant categories.

---

## Features

- **Thai Payment Slip Parsing**: Extracts transaction **Date**, **Receiver**, and **Amount (THB)** from upload slip images using EasyOCR (supporting both Thai and English).
- **Intelligent Spatial Rules**: Isolates the receiver name by bypassing sender names and bank logo details on the slip using relative bounding box geometries.
- **Auto-Categorization**: Automatically assigns transaction categories (e.g., Dining, Groceries, transport) by matching extracted receiver names against labeling configuration rules.
- **Inline Editing & Auto-Saving**: Modify dates, amounts, and categories directly in the transactions table. Editing a category automatically updates and saves the label rule to the server backend.
- **Label Manager UI**: A dedicated interface to view, filter, add, edit, and delete category rules.
- **Coverage Statistics**: Tracks batch upload summaries, comparing file upload count to successfully parsed transactions, listing any failed files with detailed error codes.
- **Visual Analytics**: Interactive charts showing spending totals, per-category averages, and top spending trends.

---

## Tech Stack

- **Backend**: Python, FastAPI, EasyOCR, PyTorch, Levenshtein distance string matching (`thefuzz`).
- **Frontend**: React (Vite), Tailwind CSS (v4), React Router DOM (v7), Lucide Icons, Recharts.

---

## Setup & Running Guide

### 1. Backend Setup

Prerequisites: Python 3.10+ (using a Conda environment is recommended).

1. Open your terminal and create a new Conda environment:
   ```bash
   conda create -n slip-detector python=3.10 -y
   ```
2. Activate the environment:
   ```bash
   conda activate slip-detector
   ```
3. Navigate to the backend folder and install the required Python packages:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
4. Run the FastAPI development server:
   ```bash
   python main.py
   ```
   The backend API will run at `http://localhost:8000`.

### 2. Frontend Setup

1. In a new terminal tab, navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install node dependencies:
   ```bash
   npm install
   ```
3. Start the Vite React development server:
   ```bash
   npm run dev
   ```
   Open the browser at `http://localhost:5173` (or the URL printed in the terminal).

---

## LLM Configuration & Auto-Categorization

This application supports automatic categorization for unseen/new receiver names using a hybrid approach:
1. **Local Heuristics**: Instantly detects common prefixes (like นาย, นาง, น.ส., Mr., Mrs.) to categorize as `Personal Transfer`, and matches keywords for categories like `Dining`, `Groceries`, `Transport`, `Utilities`, and `Credit Card Settlement`.
2. **Cloud LLM APIs (Gemini & OpenAI)**: To improve accuracy for arbitrary names, you can enable either Google's Gemini API or OpenAI's API. Since it runs in the cloud, it uses 0 MB of local RAM.

To set up:
1. Copy `backend/.env.example` to `backend/.env`.
2. Edit `backend/.env` and configure your API keys:
   ```env
   LLM_PROVIDER=gemini # Use 'gemini' or 'openai'
   GEMINI_API_KEY=your-gemini-key
   OPENAI_API_KEY=your-openai-key
   ```
3. Restart the backend server. 

Successful LLM classifications are automatically cached in the local configuration file to avoid duplicate API charges.

---

## Category Configurations

Categories are persisted locally on the backend in `backend/config/categories.json`. The file updates dynamically in real-time when label mapping changes are submitted in the frontend **Manage Labels** dashboard.
