from tkinter import *
from tkinter import ttk, messagebox

processes = []
process_count = 0

def create_frames(root):
  input_frame = Frame(root, name="input_frame", bg="#f0f0f0", padx=10, pady=10)
  input_frame.pack(fill="x")
  
  table_frame = Frame(root, name="table_frame", bg="#f0f0f0", padx=10, pady=10)
  table_frame.pack(fill="x")
  
  buttons_frame = Frame(root, name="buttons_frame", bg="#f0f0f0", padx=10, pady=10)
  buttons_frame.pack(fill="x")
  
  results_frame = Frame(root, name="results_frame", bg="#f0f0f0", padx=10, pady=10)
  results_frame.pack(fill="both", expand=True)

def create_input_fields(root):
  input_frame = root.nametowidget("input_frame")

  title_label = Label(input_frame, text="Process Details", font=("Arial", 14, "bold"))
  title_label.grid(row=0, column=0, columnspan=6, pady=10, sticky="w")
  
  Label(input_frame, text="Arrival Time:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
  arrival_time_entry = Entry(input_frame, name="arrival_time_var", width=10)
  arrival_time_entry.grid(row=1, column=1, padx=5, pady=5)

  Label(input_frame, text="Burst Time:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
  burst_time_entry = Entry(input_frame, name="burst_time_var", width=10)
  burst_time_entry.grid(row=1, column=3, padx=5, pady=5)

  Label(input_frame, text="Priority:").grid(row=1, column=4, padx=5, pady=5, sticky="e")
  priority_entry = Entry(input_frame, name="priority_var", width=10)
  priority_entry.grid(row=1, column=5, padx=5, pady=5)

def create_process_table(root):
  table_frame = root.nametowidget("table_frame")

  columns = ("Process ID", "Arrival Time", "Burst Time", "Priority")
  process_table = ttk.Treeview(table_frame, name="process_table", columns=columns, show="headings", height=10)
  
  for col in columns:
    process_table.heading(col, text=col)
    process_table.column(col, width=100, anchor="center")
  
  scrollbar = Scrollbar(table_frame, orient="vertical", command=process_table.yview)
  process_table.configure(yscrollcommand=scrollbar.set)
  
  process_table.pack(side="left", fill="both", expand=True)
  scrollbar.pack(side="right", fill="y")

def create_buttons(root):
  buttons_frame = root.nametowidget("buttons_frame")
  input_frame = root.nametowidget("input_frame")
  table_frame = root.nametowidget("table_frame")
  
  add_btn = Button(buttons_frame, command=lambda: add_process(input_frame, table_frame),  text="Add New Process", bg="green", fg="white", cursor="hand2", padx=10, pady=5)
  add_btn.pack(side="left", padx=10)
  
  calc_btn = Button(buttons_frame, command=lambda: calculate_schedule(root), text="Calculate",  bg="blue", fg="white", cursor="hand2", padx=10, pady=5)
  calc_btn.pack(side="left", padx=10)
  
  clear_btn = Button(buttons_frame, command=lambda: clear_all(root), text="Clear All",  bg="red", fg="white", cursor="hand2", padx=10, pady=5)
  clear_btn.pack(side="left", padx=10)

def create_results_area(root):
  results_frame = root.nametowidget("results_frame")

  Label(results_frame, text="Gantt Chart", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(anchor="w", pady=(10, 5))

  gantt_chart_Frame = Frame(results_frame, name="gantt_chart_Frame", height=50, bg="white")
  gantt_chart_Frame.pack(fill="x", padx=10, pady=5)

  stats_frame = Frame(results_frame, name="stats_frame", bg="#f0f0f0")
  stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
  
  columns = ("Process ID", "Completion Time", "Turnaround Time", "Waiting Time")
  results_table = ttk.Treeview(stats_frame, name="results_table", columns=columns, show="headings", height=10)
  
  for col in columns:
    results_table.heading(col, text=col)
    results_table.column(col, width=120, anchor="center")
  
  scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=results_table.yview)
  results_table.configure(yscrollcommand=scrollbar.set)
  
  results_table.pack(side="left", fill="both", expand=True)
  scrollbar.pack(side="right", fill="y")
  
  avg_stats_label = Label(stats_frame, name="avg_stats_label", text="", font=("Arial", 10), bg="#f0f0f0", justify="left")
  avg_stats_label.pack(anchor="w", pady=10)

def calculate_schedule(root):
  global processes
  if not processes:
    messagebox.showinfo("No Processes", "Please add at least one process")
    return
      
  # Make a deep copy of processes to avoid modifying the original data
  # processes = copy.deepcopy(processes)
  
  # Sort processes by arrival time
  processes.sort(key=lambda x: x["arrival_time"])
  
  # Initialize variables
  current_time = 0
  completed_processes = 0
  total_processes = len(processes)
  completion_times = {}
  gantt_chart = []
  
  # Initialize remaining time for each process
  for process in processes:
    process["remaining_time"] = process["burst_time"]
  
  # Create ready queue
  ready_queue = []
  current_process = None
  
  # Process until all processes are completed
  while completed_processes < total_processes:
    # Check for newly arrived processes
    for process in processes:
      if (process["arrival_time"] <= current_time and process["remaining_time"] > 0 and process not in ready_queue and process != current_process):
        ready_queue.append(process)
    
    # Sort ready queue by priority (lower value = higher priority)
    ready_queue.sort(key=lambda x: x["priority"])
    
    # If there's a current process and a higher priority process has arrived, preempt
    if current_process and ready_queue and ready_queue[0]["priority"] < current_process["priority"]:
      ready_queue.append(current_process)
      # Record the execution segment for Gantt chart
      if gantt_chart and gantt_chart[-1]["process"] == current_process["id"]:
        gantt_chart[-1]["end"] = current_time
      else:
        gantt_chart.append({
          "process": current_process["id"],
          "start": current_time - 1,  # -1 because we've already incremented
          "end": current_time
        })
      current_process = None
    
    # If no current process, get the highest priority process from ready queue
    if not current_process and ready_queue:
      current_process = ready_queue.pop(0)
      if not gantt_chart or gantt_chart[-1]["process"] != current_process["id"]:
        gantt_chart.append({
          "process": current_process["id"],
          "start": current_time,
          "end": None  # Will be set when process is preempted or completed
        })
  
    # If there's a current process, execute it for one time unit
    if current_process:
      current_process["remaining_time"] -= 1
      
      # If process is completed
      if current_process["remaining_time"] == 0:
        completed_processes += 1
        completion_times[current_process["id"]] = current_time + 1
        # Update Gantt chart entry
        gantt_chart[-1]["end"] = current_time + 1
        current_process = None

    # If no process is available at this time
    if not current_process and not ready_queue:
      # Find the next arriving process
      next_arrival = float('inf')
      for process in processes:
        if process["remaining_time"] > 0 and process["arrival_time"] > current_time:
          next_arrival = min(next_arrival, process["arrival_time"])
      
      if next_arrival != float('inf'):
        if gantt_chart and gantt_chart[-1]["process"] == "idle":
          gantt_chart[-1]["end"] = next_arrival
        else:
          gantt_chart.append({
            "process": "idle",
            "start": current_time,
            "end": next_arrival
          })
        current_time = next_arrival
        continue
    
    # Increment time
    current_time += 1
  
  # Calculate metrics
  display_results(root, processes, completion_times, gantt_chart)

def add_process(input_frame, table_frame):
  arrival_time_var = input_frame.nametowidget("arrival_time_var")
  burst_time_var = input_frame.nametowidget("burst_time_var")
  priority_var = input_frame.nametowidget("priority_var")
  process_table = table_frame.nametowidget("process_table")
  try:
    arrival_time = float(arrival_time_var.get())
    burst_time = float(burst_time_var.get())
    priority = int(priority_var.get())
    
    if burst_time <= 0:
      messagebox.showerror("Invalid data", "Burst time must be greater than 0")
      return
        
    if arrival_time < 0:
      messagebox.showerror("Invalid data", "Arrival time must be greater than or equal 0")
      return
    
    if priority < 0:
      messagebox.showerror("Invalid data", "Priority must be greater than or equal 0")
      return
    
    global process_count
    process_count += 1
    process_id = f"P{process_count}"
    
    process = {
      "id": process_id,
      "arrival_time": arrival_time,
      "burst_time": burst_time,
      "priority": priority,
      "remaining_time": burst_time
    }

    processes.append(process)
    
    process_table.insert("", "end", values=(process_id, arrival_time, burst_time, priority))

    process_table.update()
    
    arrival_time_var.delete(0, END)
    burst_time_var.delete(0, END)
    priority_var.delete(0, END)
    arrival_time_var.focus()

  except ValueError:
    messagebox.showerror("Invalid data", "Please enter valid data.")

def clear_all(root):
  process_table = root.nametowidget("table_frame").nametowidget("process_table")
  gantt_chart_Frame = root.nametowidget("results_frame").nametowidget("gantt_chart_Frame")
  results_table = root.nametowidget("results_frame").nametowidget("stats_frame").nametowidget("results_table")
  avg_stats_label = root.nametowidget("results_frame").nametowidget("stats_frame").nametowidget("avg_stats_label")

  global process_count
  global processes
  process_count = 0
  processes = []
  
  for item in process_table.get_children():
    process_table.delete(item)
  for item in results_table.get_children():
    results_table.delete(item)

  for widget in gantt_chart_Frame.winfo_children():
    widget.destroy()
  avg_stats_label.config(text="")
  
def display_results(root, processes, completion_times, gantt_chart):
  gantt_chart_Frame = root.nametowidget("results_frame").nametowidget("gantt_chart_Frame")
  results_table = root.nametowidget("results_frame").nametowidget("stats_frame").nametowidget("results_table")
  avg_stats_label = root.nametowidget("results_frame").nametowidget("stats_frame").nametowidget("avg_stats_label")

  for item in results_table.get_children():
    results_table.delete(item)
      
  total_turnaround_time = 0
  total_waiting_time = 0

  for process in processes:
    process_id = process["id"]
    completion_time = completion_times[process_id]
    turnaround_time = completion_time - process["arrival_time"]
    waiting_time = turnaround_time - process["burst_time"]
    
    total_turnaround_time += turnaround_time
    total_waiting_time += waiting_time
    
    results_table.insert("", "end", values=(
      process_id, completion_time, turnaround_time, waiting_time
    ))
      
  avg_turnaround_time = total_turnaround_time / len(processes)
  avg_waiting_time = total_waiting_time / len(processes)
  
  avg_stats_label.config(text=(
    f"Average Turnaround Time: {avg_turnaround_time:.2f}\n"
    f"Average Waiting Time: {avg_waiting_time:.2f}"
  ))
  
  if not gantt_chart:
    return
  
  end_time = max(segment["end"] for segment in gantt_chart)

  for time in range(0, int(end_time)):
    gantt_chart_Frame.grid_columnconfigure(time,weight=1)

  
  colors = ["lightgreen", "lightcoral", "lightblue", "lightyellow", "lightpurple", "wheat", "green", "red"]
  process_colors = {}
  
  for segment in gantt_chart:
    process_id = segment["process"]
    start = segment["start"]
    end = segment["end"]
    
    if process_id not in process_colors:
      if process_id == "idle":
        process_colors[process_id] = "#CCCCCC"
      else:
        process_number = int(process_id[1:]) - 1
        process_colors[process_id] = colors[process_number % len(colors)]

    process_label = Label(gantt_chart_Frame, text=process_id, bg=process_colors[process_id], padx=5, pady=5, font=("Arial", 12, "bold"))
    process_label.grid(row=0, column=int(start), columnspan=int(end-start), sticky="nsew")

    process_label_start = Label(process_label, bg=process_colors[process_id], text=start, font=("Arial", 7, "bold"))
    process_label_start.place(anchor="sw", relx=0, rely=1)
    process_label_end = Label(process_label, bg=process_colors[process_id], text=end, font=("Arial", 7, "bold"))
    process_label_end.place(anchor="se", relx=1, rely=1)




root = Tk()
root.title("Preemptive Praority Scheduler Simulation")
# root.geometry("900x700")
root.state('zoomed')

create_frames(root)
create_input_fields(root)
create_process_table(root)
create_buttons(root)
create_results_area(root)

root.mainloop()