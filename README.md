# AI Research & Productivity Dashboard

A multi-page **Streamlit** application that combines several practical AI tools into one clean dashboard.  
This project is designed for **students, researchers, and daily productivity use**. It includes tools for:

- Study Chat
- Paper Summary with Q&A
- Math Solver
- Code Assistant
- Weather
- Place Finder
- News Insights

The app uses **Groq models**, optional **Hugging Face models** on selected pages, free external APIs, and a consistent custom UI theme across all pages.

---

# Project Overview

This project is a **personal AI dashboard** built with **Streamlit**.  
The idea is simple: instead of building one single chatbot, this project creates a **dashboard of multiple AI-powered tools** inside one app.

The first page works like a **homepage/dashboard**, and each box opens a specific tool page.

The main goal of this project is to combine:

- **LLM-based chat**
- **document summarization**
- **content-based Q&A**
- **math solving**
- **coding help**
- **weather lookup**
- **location search**
- **news analysis**

into one structured and good-looking web app.

---

# Main Features

## 1. Study Chat
A chatbot page for general academic and study-related questions.

**What it does**
- Lets the user ask questions in a chat format
- Uses Groq models for fast responses
- Keeps chat history in the current session
- Supports theme switching
- Supports model selection
- Supports reset and delete options

**Best for**
- Study help
- research-related questions
- concept explanation
- academic brainstorming

---

## 2. Paper Summary with Q&A
A content assistant page that can summarize and answer questions from:

- pasted text
- uploaded PDF
- website URL
- YouTube link transcript

**What it does**
- extracts content from the selected source
- generates summaries in different styles
- lets the user ask questions based only on the loaded content
- acts like a simple document/link assistant

**Summary styles**
- Short Summary
- Detailed Summary
- Bullet Points
- Explain Like a Student

**Best for**
- research papers
- lecture notes
- articles
- blog posts
- YouTube educational videos

---

## 3. Math Solver
A chatbot page focused on math and statistics.

**What it does**
- solves problems step by step
- explains statistical concepts
- helps with probability, algebra, calculus, and linear algebra
- keeps chat session history

**Best for**
- university assignments
- exam preparation
- formula explanation
- statistics learning

---

## 4. Code Assistant
A coding-focused chatbot page.

**What it does**
- generates code
- explains code
- helps debug code
- helps with Streamlit, Python, SQL, JavaScript, and ML-related code
- returns formatted answers in chat

**Best for**
- coding help
- debugging
- project development
- learning programming concepts

---

## 5. Weather 
A weather page that combines a real weather API with AI explanation.

**What it does**
- searches weather by city
- fetches live weather from Open-Meteo
- shows current weather
- shows 3-day forecast
- uses AI to generate a human-friendly weather summary
- supports Groq and Hugging Face provider selection on this page

**Best for**
- daily use
- travel planning
- quick weather understanding

---

## 6. Place Finder
A location search page with map and AI summary.

**What it does**
- searches a place using OpenStreetMap Nominatim
- shows coordinates
- shows address details
- displays a map
- creates a short AI explanation of the place
- supports Groq and Hugging Face provider selection on this page

**Best for**
- travel and navigation support
- location lookup
- city/place exploration

---

## 7. News Insights
A news analysis page using NewsAPI and LLM summarization.

**What it does**
- searches for a news topic
- fetches recent articles
- shows the list of articles
- generates an AI analysis of the current news trend
- supports Groq and Hugging Face provider selection on this page

**Best for**
- following current trends
- AI news
- market/news analysis
- topic-based news reading

---

# UI / Design Concept

A major focus of this project is not only functionality but also **clean interface design**.

All major pages were updated to follow the same design system:

- same page layout
- same top bar structure
- same right control panel
- same theme system
- same styling rules
- same visual spacing and dashboard feel

The project includes **3 themes**:

- `Cloud (Light)`
- `Midnight (Dark)`
- `Night Mode`

This makes the entire app look consistent and more professional.

---

# Models Used

## Groq & Hugging Face Models
These models are used across different pages:

```python
GROQ_MODELS = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 3.1 8B": "llama-3.1-8b-instant",
    "GPT-OSS 120B": "openai/gpt-oss-120b",
    "GPT-OSS 20B": "openai/gpt-oss-20b",
}

HF_MODELS = {
    "Qwen 2.5 7B Instruct": "Qwen/Qwen2.5-7B-Instruct"
}
