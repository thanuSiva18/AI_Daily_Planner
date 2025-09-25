import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import os
from dotenv import load_dotenv

# Import modular components
from utils.ai_scheduler import generate_schedule
from utils.data_handler import (
    save_planning_data, 
    load_tasks_data, 
    save_schedule, 
    load_schedule_data
)

from utils.visualization import create_gantt_chart, create_time_distribution_chart

# Import file path constants
from constants import SCHEDULE_FILE, TASKS_FILE

# Load environment variables (for local development)
load_dotenv()

# --- Configuration and State Management ---

st.set_page_config(
    page_title="AI Daily Planner",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for task list
if 'tasks' not in st.session_state:
    st.session_state.tasks = load_tasks_data()

# Initialize session state for schedule (optional, useful for display persistence)
if 'schedule' not in st.session_state:
    st.session_state.schedule = load_schedule_data()

# --- Utility Functions ---

def add_task(name: str, duration: int, priority: str):
    """Adds a new task to the session state and resets the form."""
    if name and duration > 0:
        st.session_state.tasks.append({
            'name': name,
            'duration_min': duration,
            'priority': priority
        })
    # Input fields are cleared by st.form(clear_on_submit=True)
    else:
        st.error("Please enter a valid task name and a positive duration.")

def run_scheduler(tasks: list, start_t: time, end_t: time):
    """Executes the AI scheduling process."""
    if not tasks:
        st.warning("Please add tasks before generating a schedule.")
        return

    # 1. Format inputs for the AI module
    start_str = start_t.strftime("%H:%M")
    end_str = end_t.strftime("%H:%M")
    
    # 2. Save input data (Daily Log)
    save_planning_data(tasks, start_str, end_str)

    with st.spinner("🧠 AI is optimizing your daily schedule..."):
        # 3. Call the AI scheduler
        scheduled_tasks, message = generate_schedule(tasks, start_str, end_str)
        
        if scheduled_tasks:
            st.session_state.schedule = scheduled_tasks
            save_schedule(scheduled_tasks, message) # Save generated schedule (Daily Log)
            st.success(f"Schedule generated successfully! {message}")
        else:
            st.error(f"Scheduling failed: {message}")
            st.session_state.schedule = []


def delete_task(index: int):
    """Deletes a task from the session state list."""
    if 0 <= index < len(st.session_state.tasks):
        st.session_state.tasks.pop(index)

# --- UI Layout ---

st.title("🤖 AI Daily Planner")
st.markdown(
    """
    Plan your day by listing your tasks and available time. Our AI will generate an **optimized,
    non-overlapping schedule** prioritizing high-priority items.
    """
)

# --- API Key Check ---
# IMPORTANT: This key must be set as an environment variable (e.g., Streamlit Secrets)
if not os.getenv("GEMINI_API_KEY"):
    st.error("⚠️ **GEMINI_API_KEY** environment variable is not set.")
    st.info("Please set your API key in the environment or Streamlit Secrets panel to use the AI functionality.")
    
st.divider()

# --- 1. Task Input Form & Time Window ---

col_time, col_tasks = st.columns([1, 2])

with col_time:
    st.header("1. Time Window")
    # Default to 9:00 AM to 5:00 PM
    default_start = time(9, 0)
    default_end = time(17, 0)
    
    available_start = st.time_input("Available Start Time", value=default_start)
    available_end = st.time_input("Available End Time", value=default_end)
    
    # Input validation (must be a valid time window)
    if available_start >= available_end:
        st.error("End time must be after start time.")
        schedule_disabled = True
    else:
        schedule_disabled = False

    st.header("2. Add Tasks")
    with st.form("task_input_form", clear_on_submit=True):
        new_task_name = st.text_input("Task Name", key="task_name_input", placeholder="E.g., Finish Project Report")
        col_dur, col_prio = st.columns(2)
        
        with col_dur:
            new_task_duration = st.number_input(
                "Est. Duration (mins)", 
                min_value=1, 
                max_value=1440, # 24 hours
                value=60, 
                step=5,
                key="task_duration_input"
            )
        with col_prio:
            new_task_priority = st.selectbox(
                "Priority", 
                options=['High', 'Medium', 'Low'],
                index=1 # Default to Medium
            )
            
        submitted = st.form_submit_button("➕ Add Task to List")
        if submitted:
            add_task(new_task_name.strip(), new_task_duration, new_task_priority)
            st.rerun() # Rerun to update the task list display

with col_tasks:
    st.header(f"Task List ({len(st.session_state.tasks)} tasks)")
    if not st.session_state.tasks:
        st.info("Your task list is empty. Add tasks using the form on the left.")
    else:
        # Display tasks in a data editor for easy viewing/quick edits
        df_tasks = pd.DataFrame(st.session_state.tasks)
        df_tasks['Action'] = [f'Delete {i}' for i in range(len(df_tasks))] # Placeholder for delete action

        # Display the task table
        st.dataframe(
            df_tasks.drop(columns=['Action']), # Hide the action column in this main view
            column_order=["name", "duration_min", "priority"],
            column_config={
                "name": st.column_config.TextColumn("Task Name"),
                "duration_min": st.column_config.NumberColumn("Duration (min)", format="%d"),
                "priority": st.column_config.TextColumn("Priority")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # --- Task Deletion ---
        st.markdown("**Remove a Task:**")
        # Create a selectbox for deletion
        task_options = [f"({t['priority']}) {t['name']} - {t['duration_min']} mins" for t in st.session_state.tasks]
        
        col_del_select, col_del_btn = st.columns([3, 1])
        
        with col_del_select:
            task_to_delete_index = st.selectbox(
                "Select task to remove", 
                options=list(range(len(task_options))), 
                format_func=lambda x: task_options[x]
            )
            
        with col_del_btn:
            # Add a small vertical spacer to align the button
            st.write(" ") 
            if st.button("❌ Remove Selected Task"):
                delete_task(task_to_delete_index)
                st.rerun()

st.divider()

# --- 3. Run Scheduling ---

st.header("3. Generate Schedule")
run_button = st.button(
    "✨ Generate Optimized Daily Schedule with AI", 
    type="primary",
    disabled=schedule_disabled or not st.session_state.tasks or not os.getenv("GEMINI_API_KEY")
)

if run_button:
    run_scheduler(st.session_state.tasks, available_start, available_end)
    st.rerun()

st.divider()

# --- 4. Schedule Display and Analytics ---

st.header("4. Generated Schedule & Analytics")

if st.session_state.schedule:
    
    # 4a. Schedule Table
    st.subheader("Optimized Schedule Table")
    df_schedule = pd.DataFrame(st.session_state.schedule)
    
    # Calculate duration for the table display
    def calculate_duration(row):
        start = datetime.strptime(row['start_time'], "%H:%M")
        end = datetime.strptime(row['end_time'], "%H:%M")
        duration = (end - start).total_seconds() / 60
        return f"{int(duration)} min"

    df_schedule['Duration'] = df_schedule.apply(calculate_duration, axis=1)

    st.dataframe(
        df_schedule.drop(columns=['task_name', 'priority']).rename(columns={'task_name': 'Task', 'start_time': 'Start Time', 'end_time': 'End Time'}),
        column_order=["Start Time", "End Time", "Duration", "Task", "priority"],
        column_config={
            "task_name": st.column_config.TextColumn("Task"),
            "priority": st.column_config.TextColumn("Priority")
        },
        hide_index=True,
        use_container_width=True
    )

    # 4b. Gantt Chart Visualization
    st.subheader("Visual Timeline")
    gantt_fig = create_gantt_chart(st.session_state.schedule, available_start.strftime("%H:%M"))
    st.plotly_chart(gantt_fig, use_container_width=True)

    # 4c. Analytics
    st.subheader("Time Analytics")
    col_pie, col_stats = st.columns([1, 1])
    
    with col_pie:
        pie_fig = create_time_distribution_chart(st.session_state.schedule)
        st.plotly_chart(pie_fig, use_container_width=True)
        
    with col_stats:
        total_scheduled_time = (df_schedule['Duration'].str.replace(' min', '').astype(int)).sum()
        time_diff_min = (datetime.combine(datetime.min, available_end) - datetime.combine(datetime.min, available_start)).total_seconds() / 60
        
        st.metric("Total Available Time", f"{int(time_diff_min // 60)}h {int(time_diff_min % 60)}m")
        st.metric("Total Scheduled Time", f"{int(total_scheduled_time // 60)}h {int(total_scheduled_time % 60)}m")
        
        if time_diff_min > 0:
            utilization = (total_scheduled_time / time_diff_min) * 100
            st.metric("Time Window Utilization", f"{utilization:.1f}%")

else:
    st.info("The optimized schedule will appear here after you add tasks and click 'Generate Optimized Daily Schedule'.")

st.divider()

# --- Daily Logs Section (Simple Display) ---
st.sidebar.header("Daily Logs")
st.sidebar.info(f"Last schedule saved: `{os.path.basename(SCHEDULE_FILE)}`")

# Optional: Display content of the JSON files for debugging/log purposes
if os.path.exists(SCHEDULE_FILE):
    with open(SCHEDULE_FILE, 'r') as f:
        log_data = f.read()
    with st.sidebar.expander("View Last Schedule Log (JSON)"):
        st.json(log_data)
        
if os.path.exists(TASKS_FILE):
    with open(TASKS_FILE, 'r') as f:
        log_data = f.read()
    with st.sidebar.expander("View Last Task Input Log (JSON)"):
        st.json(log_data)