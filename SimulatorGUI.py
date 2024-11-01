import tkinter as tk
from tkinter import ttk
import json

# Global variables to hold process data and the current clock cycle
process_data = []
current_running_index = -1
waiting_times = {}
turnaround_times = {}

# Load JSON Data
def load_process_data():
    global process_data, waiting_times, turnaround_times
    with open("process_list.json", "r") as file:
        process_data = json.load(file)
    for process in process_data:
        if process["RemainingTime"] > 0:
            process["State"] = "Ready"  # Initialize all to Ready state
        # Initialize waiting and turnaround times for each process
        waiting_times[process["ProcessID"]] = 0
        turnaround_times[process["ProcessID"]] = 0

# Calculate Waiting and Turnaround Times
def update_waiting_and_turnaround_times():
    # Calculate waiting and turnaround times for each completed process
    total_waiting_time = 0
    total_turnaround_time = 0
    completed_processes = 0

    for process in process_data:
        pid = process["ProcessID"]
        burst_time = process["BurstTime"]
        if process["State"] == "Completed":
            turnaround_times[pid] = burst_time + waiting_times[pid]
            total_waiting_time += waiting_times[pid]
            total_turnaround_time += turnaround_times[pid]
            completed_processes += 1

    # Display averages
    if completed_processes > 0:
        avg_waiting_time = total_waiting_time / completed_processes
        avg_turnaround_time = total_turnaround_time / completed_processes
        average_waiting_time_label.config(text=f"Avg Waiting Time: {avg_waiting_time:.2f}")
        average_turnaround_time_label.config(text=f"Avg Turnaround Time: {avg_turnaround_time:.2f}")

# Populate each table based on the process state
def populate_tables():
    # Clear all tables first
    for table in [running_processes_table, ready_queue_table, waiting_processes_table, program_list_table]:
        table.delete(*table.get_children())
    
    # Populate each table based on the process state
    for process in process_data:
        values = (process["ProcessID"], process.get("State", ""), process["Priority"], process["BurstTime"], 
                  process["RemainingTime"], process.get("CPU", ""), process.get("Memory", ""))

        if process["State"] == "Running":
            running_processes_table.insert("", "end", values=values)
        elif process["State"] == "Ready":
            ready_queue_table.insert("", "end", values=values)
        elif process["State"] == "Waiting":
            waiting_processes_table.insert("", "end", values=values)
        
        # Add to program list with Waiting and Turnaround Times
        program_values = (process["ProcessID"], waiting_times[process["ProcessID"]], turnaround_times[process["ProcessID"]])
        program_list_table.insert("", "end", values=program_values)

    # Update average waiting and turnaround times
    update_waiting_and_turnaround_times()

# Load Process Data and Initialize GUI
def start_os():
    load_process_data()
    populate_tables()

# Move to the Next Clock Cycle
def next_clock_cycle():
    global current_running_index, process_data

    # Move the previous running process to "Ready" state if it still has remaining time
    if current_running_index != -1 and process_data[current_running_index]["RemainingTime"] > 0:
        process_data[current_running_index]["State"] = "Ready"

    # Find the next process with remaining time to run in this cycle
    found_next_process = False
    for i in range(current_running_index + 1, len(process_data)):
        if process_data[i]["RemainingTime"] > 0:
            current_running_index = i
            process_data[i]["State"] = "Running"
            found_next_process = True
            break

    # If no process was found from the current index onwards, start from the beginning of the list
    if not found_next_process:
        for i in range(len(process_data)):
            if process_data[i]["RemainingTime"] > 0:
                current_running_index = i
                process_data[i]["State"] = "Running"
                break
        else:
            # If all processes are completed, reset the running index and exit the function
            current_running_index = -1
            print("All processes have completed.")
            populate_tables()  # Update the tables one last time
            return

    # Process the current running process by reducing its RemainingTime by 1
    if current_running_index != -1:
        process = process_data[current_running_index]
        process["RemainingTime"] -= 1
        # Update waiting time for all ready processes
        for p in process_data:
            if p["State"] == "Ready":
                waiting_times[p["ProcessID"]] += 1
        # If remaining time is zero, mark it as completed
        if process["RemainingTime"] == 0:
            process["State"] = "Completed"
            current_running_index = -1  # Reset to find the next process in the next cycle

    # Refresh the tables to reflect the current process states
    populate_tables()

# Function to open a popup for creating a new process
def create_process_popup():
    popup = tk.Toplevel(root)
    popup.title("Create New Process")
    
    # Labels and entries for process attributes
    tk.Label(popup, text="Process ID:").grid(row=0, column=0, padx=5, pady=5)
    process_id_entry = tk.Entry(popup)
    process_id_entry.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(popup, text="Burst Time:").grid(row=1, column=0, padx=5, pady=5)
    burst_time_entry = tk.Entry(popup)
    burst_time_entry.grid(row=1, column=1, padx=5, pady=5)
    
    tk.Label(popup, text="Priority:").grid(row=2, column=0, padx=5, pady=5)
    priority_entry = tk.Entry(popup)
    priority_entry.grid(row=2, column=1, padx=5, pady=5)
    
    tk.Label(popup, text="Remaining Time:").grid(row=3, column=0, padx=5, pady=5)
    remaining_time_entry = tk.Entry(popup)
    remaining_time_entry.grid(row=3, column=1, padx=5, pady=5)
    
    # CPU and Memory fields (optional)
    tk.Label(popup, text="CPU:").grid(row=4, column=0, padx=5, pady=5)
    cpu_entry = tk.Entry(popup)
    cpu_entry.grid(row=4, column=1, padx=5, pady=5)
    
    tk.Label(popup, text="Memory:").grid(row=5, column=0, padx=5, pady=5)
    memory_entry = tk.Entry(popup)
    memory_entry.grid(row=5, column=1, padx=5, pady=5)
    
    # Submit button to add process
    submit_button = tk.Button(popup, text="Add Process", command=lambda: add_process(
        popup, process_id_entry.get(), burst_time_entry.get(), priority_entry.get(), 
        remaining_time_entry.get(), cpu_entry.get(), memory_entry.get()))
    submit_button.grid(row=6, column=0, columnspan=2, pady=10)

# Function to add the process to process_data and refresh tables
def add_process(popup, process_id, burst_time, priority, remaining_time, cpu, memory):
    global process_data
    # Convert input to appropriate types and add a new process to the list
    new_process = {
        "ProcessID": int(process_id),
        "BurstTime": int(burst_time),
        "Priority": int(priority),
        "RemainingTime": int(remaining_time),
        "CPU": cpu,
        "Memory": memory,
        "State": "Ready"  # New process starts in Ready state
    }
    process_data.append(new_process)
    waiting_times[new_process["ProcessID"]] = 0
    turnaround_times[new_process["ProcessID"]] = 0
    populate_tables()  # Refresh the tables to include the new process
    popup.destroy()  # Close the popup

# Create the main window
root = tk.Tk()
root.title("OS Simulator")
root.geometry("1000x700")

small_font = ("Arial", 8)

# Create the Top Block for Tables
top_block = ttk.Frame(root, width=1000)
top_block.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Table for Running Processes
running_processes_table = ttk.Treeview(top_block, columns=("Pid", "State", "Priority", "Burst", "RemainingTime", "CPU", "Memory"), height=5)
for col in running_processes_table["columns"]:
    running_processes_table.heading(col, text=col)
running_processes_table['show'] = 'headings'
running_processes_table.grid(row=1, column=0, padx=10, pady=2, sticky='w')

# Table for Ready Queue
ready_queue_table = ttk.Treeview(top_block, columns=("Pid", "State", "Priority", "Burst", "RemainingTime", "CPU", "Memory"), height=5)
for col in ready_queue_table["columns"]:
    ready_queue_table.heading(col, text=col)
ready_queue_table['show'] = 'headings'
ready_queue_table.grid(row=3, column=0, padx=10, pady=2, sticky='w')

# Table for Waiting Processes
waiting_processes_table = ttk.Treeview(top_block, columns=("Pid", "State", "Priority", "Burst", "RemainingTime", "CPU", "Memory"), height=5)
for col in waiting_processes_table["columns"]:
    waiting_processes_table.heading(col, text=col)
waiting_processes_table['show'] = 'headings'
waiting_processes_table.grid(row=5, column=0, padx=10, pady=2, sticky='w')

# Create the Bottom Block for Scheduler, OS Control, and Program List
bottom_block = ttk.Frame(root, width=1000)
bottom_block.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Scheduler Controls Section
scheduler_frame = ttk.LabelFrame(bottom_block, text="Scheduler Policies")
scheduler_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nw")

scheduler_var = tk.StringVar(value="Round Robin (RR)")  # Pre-select Round Robin
policies = ["First-Come, First-Served (FCFS)", "Shortest Job First (SJF)", "Round Robin (RR)", "Priority", "Earliest Deadline First (EDF)"]
for policy in policies:
    tk.Radiobutton(scheduler_frame, text=policy, variable=scheduler_var, value=policy).pack(anchor=tk.W)

# OS Control Section
os_control_frame = ttk.LabelFrame(bottom_block, text="OS Control")
os_control_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nw")

start_button = tk.Button(os_control_frame, text="Start", width=15, command=start_os)
start_button.pack(padx=5, pady=5)

suspend_button = tk.Button(os_control_frame, text="Suspend", width=15)
suspend_button.pack(padx=5, pady=5)

# Next Clock Button to control clock cycle
next_clock_button = tk.Button(os_control_frame, text="Next Clock", width=15, command=next_clock_cycle)
next_clock_button.pack(padx=5, pady=5)

# Program List Section
program_list_frame = ttk.LabelFrame(bottom_block, text="Program List")
program_list_frame.grid(row=0, column=2, padx=10, pady=5, sticky="nw")

# Table to display ProcessID, Waiting Time, and Turnaround Time
program_list_table = ttk.Treeview(program_list_frame, columns=("ProcessID", "Waiting Time", "Turnaround Time"), height=5)
program_list_table.heading("ProcessID", text="Process ID")
program_list_table.heading("Waiting Time", text="Waiting Time")
program_list_table.heading("Turnaround Time", text="Turnaround Time")
program_list_table['show'] = 'headings'
program_list_table.pack(pady=5)

# Labels to display average waiting and turnaround times
average_waiting_time_label = tk.Label(program_list_frame, text="Avg Waiting Time: 0", font=small_font)
average_waiting_time_label.pack()

average_turnaround_time_label = tk.Label(program_list_frame, text="Avg Turnaround Time: 0", font=small_font)
average_turnaround_time_label.pack()

# Control Buttons Section
control_frame = tk.Frame(bottom_block)
control_frame.grid(row=1, column=0, pady=5, padx=5, sticky="w")

clear_button = tk.Button(control_frame, text="CLEAR", width=10, font=small_font)
clear_button.grid(row=0, column=0, padx=5)

remove_button = tk.Button(control_frame, text="REMOVE", width=10, font=small_font)
remove_button.grid(row=0, column=1, padx=5)

resume_button = tk.Button(control_frame, text="RESUME", width=10, font=small_font)
resume_button.grid(row=0, column=2, padx=5)

# Create Process Button to open the popup
create_process_button = tk.Button(root, text="Create Process", width=15, font=small_font, command=create_process_popup)
create_process_button.pack(side=tk.BOTTOM, anchor=tk.SE, padx=20, pady=10)

# Run the application
root.mainloop()
