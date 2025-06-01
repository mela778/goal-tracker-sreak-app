import json
import datetime
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# Embedding or exportable files
*.embed.html text eol=lf
*.trinket    text eol=lf  # custom extension, if used
# Constants
CATEGORIES = ['Health', 'Work', 'Learning', 'Finance', 'Personal Development', 'Other']
GOAL_TYPES = ['Daily', 'Weekly', 'Monthly', 'Yearly', 'Other']

# Data containers
goal_data = {}
completed_goals = {}
current_streaks = {}
current_user = None

# Load and save

def save_data():
    if not current_user:
        return
    filename = f'{current_user}_goals.json'
    with open(filename, 'w') as f:
        json.dump({
            'goal_data': goal_data,
            'completed_goals': completed_goals,
            'current_streaks': current_streaks
        }, f, indent=4)

def load_user(username):
    global goal_data, completed_goals, current_streaks, current_user
    current_user = username
    filename = f'{username}_goals.json'
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            goal_data = data.get('goal_data', {})
            completed_goals = data.get('completed_goals', {})
            current_streaks = data.get('current_streaks', {})
    else:
        goal_data = {}
        completed_goals = {}
        current_streaks = {}

def export_to_csv():
    filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if filename:
        with open(filename, 'w') as f:
            f.write("Goal,Description,Category,Type,Streak,Deadline\n")
            for name, g in goal_data.items():
                deadline = g.get('deadline', '')
                f.write(f"{name},{g['description']},{g['category']},{g['type']},{current_streaks.get(name, 0)},{deadline}\n")
        messagebox.showinfo("Exported", f"Goals exported to {filename}")

# Modern themed window with padding & card style container
def themed_window(title):
    win = tk.Toplevel(root)
    win.title(title)
    win.configure(bg='#f5f7fa')  # light modern background
    win.geometry('600x400')
    container = ttk.Frame(win, padding=15, style='Card.TFrame')
    container.pack(fill='both', expand=True, padx=10, pady=10)
    win.container = container
    return win

def add_goal_window():
    def save_goal():
        name = entry_title.get().strip()
        if not name:
            messagebox.showwarning('Warning', 'Title cannot be empty!')
            return
        if name in goal_data:
            messagebox.showwarning('Warning', 'Goal title must be unique!')
            return
        goal_data[name] = {
            'description': entry_desc.get().strip(),
            'type': combo_type.get(),
            'category': combo_category.get(),
            'deadline': entry_deadline.get().strip(),
            'notes': entry_notes.get().strip(),
            'added_on': datetime.date.today().isoformat()
        }
        completed_goals[name] = []
        current_streaks[name] = 0
        save_data()
        messagebox.showinfo('Success', f'Goal "{name}" added!')
        win.destroy()

    win = themed_window('Add Goal')
    form_frame = ttk.Frame(win.container)
    form_frame.pack(fill='both', expand=True)

    fields = [
        ('Title:', tk.Entry(form_frame, width=40)),
        ('Description:', tk.Entry(form_frame, width=40)),
        ('Goal Type:', ttk.Combobox(form_frame, values=GOAL_TYPES, width=37)),
        ('Category:', ttk.Combobox(form_frame, values=CATEGORIES, width=37)),
        ('Deadline (YYYY-MM-DD):', tk.Entry(form_frame, width=40)),
        ('Notes:', tk.Entry(form_frame, width=40))
    ]

    for i, (label, widget) in enumerate(fields):
        ttk.Label(form_frame, text=label, font=('Segoe UI', 10)).grid(row=i, column=0, sticky='w', pady=8)
        widget.grid(row=i, column=1, pady=8)

    entry_title, entry_desc, combo_type, combo_category, entry_deadline, entry_notes = [w for _, w in fields]
    combo_type.current(0)
    combo_category.current(0)

    ttk.Button(form_frame, text='Save Goal', command=save_goal, style='Accent.TButton').grid(columnspan=2, pady=15)

def view_goals_window():
    win = themed_window('Your Goals')
    canvas = tk.Canvas(win.container, bg='#f5f7fa', highlightthickness=0)
    frame = ttk.Frame(canvas)
    scrollbar = ttk.Scrollbar(win.container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=frame, anchor='nw')

    def on_frame_config(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame.bind("<Configure>", on_frame_config)

    sorted_goals = sorted(goal_data.items(), key=lambda x: x[0].lower())  # Alphabetically ignoring case

    for name, goal in sorted_goals:
        card = ttk.LabelFrame(frame, text=name, padding=15, style='Card.TLabelframe')
        card.pack(padx=15, pady=10, fill='x')

        ttk.Label(card, text=f"Description: {goal['description']}").pack(anchor='w', pady=2)
        ttk.Label(card, text=f"Type: {goal['type']} | Category: {goal['category']}").pack(anchor='w', pady=2)

        if goal.get('deadline'):
            try:
                deadline_date = datetime.datetime.strptime(goal['deadline'], '%Y-%m-%d').date()
                days_left = (deadline_date - datetime.date.today()).days
                deadline_msg = f"⏳ {days_left} days left" if days_left >= 0 else "⚠️ Overdue!"
                ttk.Label(card, text=f"Deadline: {goal['deadline']} | {deadline_msg}", foreground='#f57c00').pack(anchor='w', pady=2)
            except Exception:
                pass

        if goal.get('notes'):
            ttk.Label(card, text=f"Notes: {goal['notes']}").pack(anchor='w', pady=2)

        streak = current_streaks.get(name, 0)
        ttk.Label(card, text=f"Streak: {streak} day(s)").pack(anchor='w', pady=2)
        try:
            added_on_date = datetime.datetime.strptime(goal['added_on'], '%Y-%m-%d').date()
            total_days = (datetime.date.today() - added_on_date).days + 1
            percentage = int((streak / total_days) * 100) if total_days > 0 else 0
        except Exception:
            percentage = 0
        ttk.Label(card, text=f"Progress: {percentage}%").pack(anchor='w', pady=2)

        if streak >= 7:
            ttk.Label(card, text=f"🏅 Achievement: 7+ day streak!", foreground='#ffb300').pack(anchor='w', pady=2)

        btn_frame = ttk.Frame(card)
        btn_frame.pack(anchor='w', pady=8)

        ttk.Button(btn_frame, text='Mark as Done', command=lambda n=name: complete_goal(n, win), style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Show Progress', command=lambda n=name: show_progress_chart(n), style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(btn_frame, text='View History', command=lambda n=name: view_history(n), style='Accent.TButton').pack(side='left', padx=5)

def complete_goal(goal_name, window=None):
    today = datetime.date.today().isoformat()
    if today in completed_goals.get(goal_name, []):
        messagebox.showinfo('Info', 'Goal already marked today.')
        return
    completed_goals.setdefault(goal_name, []).append(today)
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    if yesterday in completed_goals.get(goal_name, []):
        current_streaks[goal_name] = current_streaks.get(goal_name, 0) + 1
    else:
        current_streaks[goal_name] = 1
    save_data()
    messagebox.showinfo('Done', f'"{goal_name}" marked as done for today!')
    if window:
        window.destroy()
        view_goals_window()

def show_progress_chart(goal_name):
    today = datetime.date.today()
    last_7_days = [(today - datetime.timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
    completions = completed_goals.get(goal_name, [])
    statuses = [1 if day in completions else 0 for day in last_7_days]

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(last_7_days, statuses, color=['#4caf50' if s else '#e0e0e0' for s in statuses], edgecolor='none')
    ax.set_title(f"Progress: {goal_name}", fontsize=14, fontweight='bold', color='#1976d2')
    ax.set_ylim(0, 1.2)
    ax.set_ylabel('Done (1=Yes)', fontsize=11, color='#333')
    ax.set_xticklabels(last_7_days, rotation=45, ha='right', fontsize=9, color='#555')
    ax.set_yticks([])

    chart_win = themed_window(f'Progress Chart - {goal_name}')
    canvas = FigureCanvasTkAgg(fig, master=chart_win.container)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

def view_history(goal_name):
    win = themed_window(f'History for {goal_name}')
    history = completed_goals.get(goal_name, [])
    history_text = "\n".join(sorted(history))
    text_box = tk.Text(win.container, height=15, wrap='word', font=('Segoe UI', 11), bg='white', fg='#333')
    text_box.insert('1.0', history_text or "No history yet.")
    text_box.config(state='disabled')
    text_box.pack(fill='both', expand=True)

def show_dashboard():
    win = themed_window('Dashboard Summary')
    total_goals = len(goal_data)
    completed_today = sum(1 for completions in completed_goals.values() if datetime.date.today().isoformat() in completions)
    longest_streak = max(current_streaks.values()) if current_streaks else 0

    summary = (
        f"Total Goals: {total_goals}\n"
        f"Goals Completed Today: {completed_today}\n"
        f"Longest Streak: {longest_streak} day(s)"
    )
    ttk.Label(win.container, text=summary, font=('Segoe UI', 14)).pack(pady=20)

def show_calendar():
    win = themed_window('Calendar View')
    # Very simple calendar display, can be enhanced later
    cal_text = ""
    today = datetime.date.today()
    for i in range(-3, 4):
        day = today + datetime.timedelta(days=i)
        day_str = day.isoformat()
        done_goals = [g for g, dlist in completed_goals.items() if day_str in dlist]
        cal_text += f"{day_str}: {', '.join(done_goals) if done_goals else 'No goals completed'}\n"

    text_box = tk.Text(win.container, height=15, wrap='word', font=('Segoe UI', 11), bg='white', fg='#333')
    text_box.insert('1.0', cal_text)
    text_box.config(state='disabled')
    text_box.pack(fill='both', expand=True)

def start_main_app():
    global root
    root = tk.Tk()
    root.title('🎯 Modern Goal Tracker')
    root.geometry('800x600')
    root.configure(bg='#f5f7fa')  # soft background color

    style = ttk.Style()
    style.theme_use('clam')

    style.configure('TLabel', background='#f5f7fa', foreground='#333', font=('Segoe UI', 11))
    style.configure('Header.TLabel', font=('Segoe UI', 20, 'bold'), foreground='#1976d2', background='#f5f7fa')
    style.configure('TButton', font=('Segoe UI', 11, 'bold'), padding=8, background='#1976d2', foreground='white', borderwidth=0)
    style.map('TButton',
              background=[('active', '#1565c0'), ('!disabled', '#1976d2')],
              foreground=[('active', 'white'), ('!disabled', 'white')])

    style.configure('Card.TFrame', background='white', relief='raised', borderwidth=1)
    style.configure('Card.TLabelframe', background='white', relief='raised', borderwidth=1, font=('Segoe UI', 12, 'bold'))
    style.configure('TEntry', fieldbackground='white', foreground='#333')
    style.configure('TCombobox', fieldbackground='white', foreground='#333')

    # Accent style for buttons
    style.configure('Accent.TButton', background='#1976d2', foreground='white', padding=10, font=('Segoe UI', 11, 'bold'))
    style.map('Accent.TButton',
              background=[('active', '#1565c0')],
              foreground=[('active', 'white')])

    ttk.Label(root, text='🎯 Modern Goal Tracker', style='Header.TLabel').pack(pady=(20, 30))

    btn_frame = ttk.Frame(root, padding=10, style='TFrame')
    btn_frame.pack(pady=10)

    buttons = [
        ('Add New Goal', add_goal_window),
        ('View Your Goals', view_goals_window),
        ('Dashboard Summary', show_dashboard),
        ('Calendar View', show_calendar),
        ('Export to CSV', export_to_csv),
        ('Exit', root.destroy)
    ]

    for (text, cmd) in buttons:
        btn = ttk.Button(btn_frame, text=text, command=cmd, width=25, style='Accent.TButton')
        btn.pack(pady=8)

    root.mainloop()

def login_window():
    def login():
        username = entry.get().strip()
        if not username:
            messagebox.showwarning('Warning', 'Please enter a username.')
            return
        load_user(username)
        login_win.destroy()
        start_main_app()

    login_win = tk.Tk()
    login_win.title('Login')
    login_win.geometry('400x200')
    login_win.configure(bg='#f5f7fa')

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TLabel', background='#f5f7fa', foreground='#333', font=('Segoe UI', 12))
    style.configure('TEntry', font=('Segoe UI', 12), fieldbackground='white', foreground='#333')
    style.configure('Accent.TButton', background='#1976d2', foreground='white', padding=8, font=('Segoe UI', 11, 'bold'))
    style.map('Accent.TButton',
              background=[('active', '#1565c0')],
              foreground=[('active', 'white')])

    ttk.Label(login_win, text='Enter Username:', font=('Segoe UI', 14)).pack(pady=20)
    entry = ttk.Entry(login_win, font=('Segoe UI', 14), width=25)
    entry.pack(pady=10)
    ttk.Button(login_win, text='Login', command=login, style='Accent.TButton').pack(pady=20)

    login_win.mainloop()

if __name__ == '__main__':
    login_window()
