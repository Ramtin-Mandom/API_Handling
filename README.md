# Paper Summary Studio
## Multi-Prompt Academic Paper Summarization System using FastAPI and OpenAI

## Introduction

This is a personal project I built to practice working with self-made APIs and OpenAI’s API.  
To use this project, you will need your own OpenAI API key and available tokens.

---

## Summary

This is a Python application that summarizes academic papers using multiple prompts (one API call per prompt), then evaluates all generated summaries using OpenAI, selects the best summary, and returns it to the user.

Both input and output can be handled as TXT or PDF files.

---

## Problem Solved

Academic papers tend to be long and difficult to review quickly. When working on a project and evaluating multiple papers before deciding which ones to use, it can be more efficient to first read summaries and determine whether a paper is worth deeper study.

One advantage this application has over using ChatGPT directly is consistency. The application uses a structured template for every summary, so users become familiar with how to read and compare outputs.

Additionally, the system generates five different summaries and compares them, returning the best one based on evaluation. This makes the results both more consistent and more reliable than a single direct prompt.

---

## Cost Analysis

A standard ChatGPT subscription costs approximately $20 per month.

This application costs approximately **4.6 cents per 10,000 words** using **GPT-4.1 Mini**.

Depending on usage needs, this may be a more cost-efficient option.

---

## Features

- FastAPI backend for paper summarization requests  
- Multi-prompt OpenAI summarization pipeline  
- LLM-based evaluation to choose the strongest summary  
- PDF-to-text extraction  
- Text-to-PDF export with formatting rules  
- Desktop GUI built with Tkinter  
- TXT and PDF export options  
- Pydantic validation models  
- Custom exception handling  
- Unit testing with pytest  

---

## System Architecture

```text
Input Paper
   ↓
Preprocessing
   ↓
5 Prompt Variations
   ↓
5 OpenAI Summary Calls
   ↓
Evaluation Prompt (chooses best summary)
   ↓
Final Summary Selection
   ↓
API Response / GUI Output / Export
```

---

## Project Structure

```text
project_root/
│
├── app/
│   ├── myAPI.py
│   ├── services.py
│   ├── models.py
│   ├── prompts.py
│   └── pdf_converter.py
│
├── UI_application.py
│
├── tests/
│   ├── test_services.py
│   └── test_myAPI.py
│
├── sample_data/
│   ├── inputs/
│   └── outputs/
│
├── requirements.txt
└── README.md
```

---

## How to Run the Project

**Requires Python 3.10 or higher**

```bash
git clone <repo-url>
cd PaperSummaryStudio

python -m venv .venv

# Linux / Mac
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\activate.ps1

pip install -r requirements.txt
```

Create a `.env` file and add:

```bash
OPENAI_API_KEY=your_api_key
```

---

## Running the API

```bash
uvicorn app.myAPI:app --reload
```

Test the API at:

```text
http://127.0.0.1:8000/docs
```

---

## Running the Application

```bash
python UI_application.py
```

---

## Testing and Validation

There are two test files:

- `test_services.py`  
  Unit tests for functions in `services.py`, verifying individual functionality.

- `test_myAPI.py`  
  Tests API endpoints, checks requests are handled properly, and validates behavior for invalid inputs.

Run all tests with:

```bash
pytest -v
```

---

## Author

Ramtin Rezaei  
Simon Fraser University  
2026/04/22