# 🤖 AI Daily Planner

Plan your day efficiently by listing your tasks and available time. The AI Daily Planner generates an **optimized, non-overlapping schedule** that prioritizes your most important tasks using Gemini AI.

---

## Features

- **Task Management:** Add, view, and remove tasks with estimated durations and priorities.
- **AI-Powered Scheduling:** Automatically generate an optimized daily schedule using Google Gemini AI.
- **Visual Timeline:** Interactive Gantt chart for a clear overview of your day.
- **Time Analytics:** Visualize your time distribution and utilization.
- **Daily Logs:** View and debug your last schedule and task input logs.

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-daily-planner.git
cd ai-daily-planner
```

### 2. Install Dependencies

It’s recommended to use a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root and add your [Gemini API key](https://ai.google.dev/) like this:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at [http://localhost:8501](http://localhost:8501).

---

## Usage

1. **Set your available time window.**
2. **Add tasks** with names, durations, and priorities.
3. **Click "Generate Optimized Daily Schedule"** to let the AI create your schedule.
4. **View your schedule, timeline, and analytics.**
5. **Check the sidebar for logs and debugging info.**

---

## Project Structure

```
.
├── app.py
├── constants.py
├── requirements.txt
├── .env
├── utils/
│   ├── ai_scheduler.py
│   ├── data_handler.py
│   └── visualization.py
├── schedule.json
├── tasks.json
└── README.md
```

---

## Troubleshooting

- **GEMINI_API_KEY not set:**  
  Make sure your `.env` file exists and contains your API key.
- **JSON Parse Error:**  
  If you see a JSON parse error in the sidebar, ensure `schedule.json` and `tasks.json` contain valid JSON (e.g., `[]` for empty).
- **No schedule generated:**  
  Ensure you have added tasks and set a valid time window.

---

## License

MIT License

---

*Built with [Streamlit](https://streamlit.io/) and [Google Gemini AI](https://ai.google.dev/).*
