# 📺 YTIntel

**YTIntel** is an AI-powered YouTube channel analyzer that helps users find the most valuable videos tailored to their personal learning goals. Instead of scrolling endlessly, YTIntel delivers a curated list of content that aligns with your intent, not just the algorithm.

---

## 🚨 Problem
YouTube is overflowing with valuable content — but when a user wants to learn something specific, finding the right videos becomes a frustrating mess.

Search results are noisy, clickbait-heavy, and popularity-driven

Channel pages contain hundreds of videos with little guidance

Even playlists, when available, are generic and not personalized

Users waste time scrolling, guessing, and getting distracted, especially when they’re just trying to follow a goal like “learn AI for research” or “build confidence”

For learners and upskillers, this is a huge productivity leak.

---

## ✅ How YTIntel Solves It
YTIntel is an intelligent YouTube channel summarizer that helps users find only the most relevant videos from any channel — based on their personal goals.

Using:

🎯 User-defined goals

📺 Channel video metadata (title, description, tags, etc.)

🤖 Gemini LLM via LangChain for deep filtering

📊 Relevance scoring and justification-based ranking

## YTIntel:

Picks only the videos that align with the user’s intent

Categorizes them meaningfully (e.g., "Foundational", "Actionable Advice", etc.)

Provides brief explanations for why each video was chosen

Filters out everything else

## In short:

YTIntel turns chaotic video libraries into goal-focused learning paths — instantly.
No playlists. No guesswork. No fluff.

---

## 🚀 Features

- 🔎 **Channel Summarization** – Quickly get a summary of the channel: name, subscribers, video count, etc.
- 🎯 **Goal-Based Filtering** – Users enter their learning goal, and YTIntel finds videos that truly match it.
- 🧠 **LLM-Powered Analysis** – Uses Gemini to deeply understand video titles, descriptions, and metadata.
- 📊 **Streamlit UI** – Clean, simple, interactive interface.
- 📷 **Video Thumbnails + Links** – Beautiful video display in YouTube style.

---

## 🛠️ Tech Stack

| Tech | Purpose |
|------|---------|
| **Python** | Core logic & backend |
| **Streamlit** | Frontend / App UI |
| **YouTube Data API v3** | Fetch channel & video metadata |
| **Gemini LLM (via LangChain)** | Video understanding and filtering |
| **Pandas** | Data wrangling |
| **isodate / datetime** | Duration parsing |

---

## ✍️ How It Works

1. **User Input**:  
   - Enters a YouTube channel ID  
   - Describes their learning goals

2. **Video Extraction**:  
   - Title, description, duration, likes, views, etc. are fetched via the YouTube API

3. **LLM Filtering**:  
   - Gemini filters and analyzes videos to find those that are *most relevant* to the user's goals

4. **Output**:  
   - Displays the selected video cards with linked thumbnails,titles, and justifications

---

## 🧪 Sample Use Cases

- **AI/ML Enthusiast**: "I want to learn core machine learning concepts for research."
- **Self-Help Seeker**: "I want to build better habits and develop discipline."
- **Student**: "I'm preparing for data structures & algorithms interviews."

> 🧠 YTIntel adapts to each intent and shows only what's useful—no clickbait, no fluff.

---

💖 Credits
Built by @Sagnik

Powered by Google's Gemini, YouTube Data API, and ✨ Streamlit magic

---

🙌 Star the repo if you found it helpful!
