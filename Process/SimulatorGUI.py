import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt

# Global variables to hold process data and the current clock cycle
process_data = []
current_running_index = -1
gantt_chart_data = []  # To store the Gantt chart data
waiting_times = {}
turnaround_times = {}

# Load JSON Data
def load_process_data():
    global process_data, waiting_times, turnaround_times
    process_data = [
        {"ProcessID": 1, "BurstTime": 6, "Priority": 2, "RemainingTime": 6, "State": "Ready", "ProgramCounter": 2, "OpenFiles": 2, "AX": 10, "BX": 20},
        {"ProcessID": 2, "BurstTime": 8, "Priority": 1, "RemainingTime": 8, "State": "Ready", "ProgramCounter": 3, "OpenFiles": 1, "AX": 15, "BX": 25},
        {"ProcessID": 3, "BurstTime": 10, "Priority": 3, "RemainingTime": 10, "State": "Ready", "ProgramCounter": 4, "OpenFiles": 0, "AX": 5, "BX": 10},
    ]
    for process in process_data:
        waiting_times[process["ProcessID"]] = 0
        turnaround_times[process["ProcessID"]] = 0

# Update PCB Section
def update_pcb(process):
    if process:
        pcb_labels["Program Counter"].set(process.get("ProgramCounter", "N/A"))
        pcb_labels["Number of Open Files"].set(process.get("OpenFiles", "N/A"))
        pcb_labels["AX"].set(process.get("AX", "N/A"))
        pcb_labels["BX"].set(process.get("BX", "N/A"))
    else:
        for key in pcb_labels:
            pcb_labels[key].set("N/A")

# Populate each table based on the process state
def populate_tables():
    # Clear all existing table entries
    for table in [running_processes_table, ready_queue_table, waiting_processes_table, program_list_table]:
        table.delete(*table.get_children())
    
    # Populate the tables with updated process states
    for process in process_data:
        values = (process["ProcessID"], process.get("State", ""), process["Priority"], process["BurstTime"], process["RemainingTime"])
        if process["State"] == "Running":
            running_processes_table.insert("", "end", values=values)
        elif process["State"] == "Ready":
            ready_queue_table.insert("", "end", values=values)
        elif process["State"] == "Blocked":  # Update for Blocked processes
            waiting_processes_table.insert("", "end", values=values)

        # Add all processes to the Program List table with waiting and turnaround times
        program_values = (process["ProcessID"], waiting_times[process["ProcessID"]], turnaround_times[process["ProcessID"]])
        program_list_table.insert("", "end", values=program_values)

    # Update average waiting and turnaround times
    update_avg_times()

# Update Average Waiting and Turnaround Times
def update_avg_times():
    total_waiting_time = sum(waiting_times.values())
    total_turnaround_time = sum(turnaround_times.values())
    num_processes = len(process_data)

    if num_processes > 0:
        avg_waiting_time = total_waiting_time / num_processes
        avg_turnaround_time = total_turnaround_time / num_processes
        average_waiting_time_label.config(text=f"Avg Waiting Time: {avg_waiting_time:.2f}")
        average_turnaround_time_label.config(text=f"Avg Turnaround Time: {avg_turnaround_time:.2f}")
    else:
        average_waiting_time_label.config(text="Avg Waiting Time: N/A")
        average_turnaround_time_label.config(text="Avg Turnaround Time: N/A")

# Update Waiting and Turnaround Times
def update_waiting_and_turnaround_times():
    global process_data, waiting_times, turnaround_times
    
    total_waiting_time = 0
    total_turnaround_time = 0
    completed_processes = 0

    for process in process_data:
        pid = process["ProcessID"]
        burst_time = process["BurstTime"]
        state = process["State"]
        
        if state == "Completed":
            turnaround_times[pid] = burst_time + waiting_times[pid]
            total_turnaround_time += turnaround_times[pid]
            total_waiting_time += waiting_times[pid]
            completed_processes += 1
        elif state == "Ready":
            waiting_times[pid] += 1

    if completed_processes > 0:
        avg_waiting_time = total_waiting_time / completed_processes
        avg_turnaround_time = total_turnaround_time / completed_processes
        average_waiting_time_label.config(text=f"Avg Waiting Time: {avg_waiting_time:.2f}")
        average_turnaround_time_label.config(text=f"Avg Turnaround Time: {avg_turnaround_time:.2f}")
    else:
        average_waiting_time_label.config(text="Avg Waiting Time: N/A")
        average_turnaround_time_label.config(text="Avg Turnaround Time: N/A")

# Start OS Simulation
def start_os():
    reset_simulation()
    load_process_data()
    populate_tables()

# Collect data for Gantt chart
def record_gantt_chart_data(clock_cycle, process_id, end_time=False):
    global gantt_chart_data
    if end_time:
        # Ensure there is an entry in the Gantt chart data to update
        if gantt_chart_data:
            gantt_chart_data[-1] = (gantt_chart_data[-1][0], gantt_chart_data[-1][1], clock_cycle)
    else:
        # Append the start time and process ID
        gantt_chart_data.append((process_id, clock_cycle))

# Move to the Next Clock Cycle
def next_clock_cycle():
    global current_running_index, process_data

    # Move the previous running process to "Ready" state if it still has remaining time
    if current_running_index != -1 and process_data[current_running_index]["RemainingTime"] > 0:
        process_data[current_running_index]["State"] = "Ready"
        record_gantt_chart_data(len(gantt_chart_data), process_data[current_running_index]["ProcessID"], end_time=True)

    # Find the next process to run
    found_next_process = False
    for i in range(current_running_index + 1, len(process_data)):
        if process_data[i]["RemainingTime"] > 0:
            # Check if the process has a valid ProgramCounter
            if process_data[i].get("ProgramCounter", 0) <= 0:
                # Move the process to Blocked state if ProgramCounter is invalid
                process_data[i]["State"] = "Blocked"
                print(f"Process {process_data[i]['ProcessID']} moved to Blocked state due to invalid ProgramCounter.")
                populate_tables()  # Refresh the GUI to show the change
                continue

            current_running_index = i
            process_data[i]["State"] = "Running"
            update_pcb(process_data[i])  # Update PCB for the running process
            found_next_process = True
            break

    # If no process was found, restart search from the beginning
    if not found_next_process:
        for i in range(len(process_data)):
            if process_data[i]["RemainingTime"] > 0:
                # Check if the process has a valid ProgramCounter
                if process_data[i].get("ProgramCounter", 0) <= 0:
                    # Move the process to Blocked state if ProgramCounter is invalid
                    process_data[i]["State"] = "Blocked"
                    print(f"Process {process_data[i]['ProcessID']} moved to Blocked state due to invalid ProgramCounter.")
                    populate_tables()  # Refresh the GUI to show the change
                    continue

                current_running_index = i
                process_data[i]["State"] = "Running"
                update_pcb(process_data[i])  # Update PCB for the running process
                found_next_process = True
                break

    # If no process can be scheduled, terminate the simulation
    if not found_next_process:
        current_running_index = -1
        update_pcb(None)  # Clear PCB when all processes are completed
        print("All processes completed.")
        show_gantt_chart()  # Show Gantt chart when simulation is complete
        return

    # Run the selected process
    if current_running_index != -1:
        process = process_data[current_running_index]
        process["RemainingTime"] -= 1
        record_gantt_chart_data(len(gantt_chart_data), process["ProcessID"])
        if process["RemainingTime"] == 0:
            process["State"] = "Completed"
            record_gantt_chart_data(len(gantt_chart_data), process["ProcessID"], end_time=True)

    # Update waiting and turnaround times
    update_waiting_and_turnaround_times()
    populate_tables()  # Refresh the GUI at the end of the cycle


def reset_simulation():
    global gantt_chart_data, current_running_index, process_data

    # Reset the Gantt chart data
    gantt_chart_data = []

    # Reset process data (reinitialize with initial state if needed)
    for process in process_data:
        process["RemainingTime"] = process["BurstTime"]  # Assuming BurstTime is the original time
        process["State"] = "New"  # Reset to initial state
        process["ProgramCounter"] = process.get("InitialProgramCounter", 0)  # Optional: Reset ProgramCounter if applicable

    # Reset the current running index
    current_running_index = -1

# Show Gantt Chart
def show_gantt_chart():
    plt.figure(figsize=(12, 2))
    plt.title("Gantt Chart")
    plt.xlabel("Clock Cycles")
    plt.yticks([1], ["Processes"])

    process_intervals = {}
    running_times = []  # To capture x-tick positions
    color_map = {1: 'tab:blue', 2: 'tab:orange', 3: 'tab:green'}  # Color mapping for processes

    # Create intervals for each process based on gantt_chart_data
    for process_id, start_time, *end_time in gantt_chart_data:
        if process_id not in process_intervals:
            process_intervals[process_id] = []
        if end_time:
            end_time = end_time[0]
            process_intervals[process_id].append((start_time, end_time))
            running_times.extend([start_time, end_time])

    # Plot each process interval on the Gantt chart
    for process_id, times in process_intervals.items():
        for start_time, end_time in times:
            plt.broken_barh([(start_time, end_time - start_time)], (0.5, 0.9),
                            facecolors=color_map.get(process_id, 'tab:gray'))
            plt.text((start_time + end_time) / 2, 1, f'P{process_id}', va='center', ha='center', color='white')

    if running_times:
        plt.xticks(range(min(running_times), max(running_times) + 1))

    plt.tight_layout()
    plt.show()

# Add Process Function
# Add Process Function
def add_process(popup, process_id, burst_time, priority, remaining_time, cpu, memory, program_counter, open_files, ax, bx):
    global process_data

    # Validate and handle empty or optional inputs
    def to_int(value, default=0):
        try:
            return int(value)
        except ValueError:
            return default

    # Add the new process to the list
    new_process = {
        "ProcessID": to_int(process_id),
        "BurstTime": to_int(burst_time),
        "Priority": to_int(priority),
        "RemainingTime": to_int(remaining_time),
        "CPU": cpu if cpu else "N/A",  # Default to "N/A" if empty
        "Memory": memory if memory else "N/A",  # Default to "N/A" if empty
        "State": "Ready",
        "ProgramCounter": to_int(program_counter),
        "OpenFiles": to_int(open_files),
        "AX": to_int(ax),
        "BX": to_int(bx),
    }

    process_data.append(new_process)
    waiting_times[new_process["ProcessID"]] = 0
    turnaround_times[new_process["ProcessID"]] = 0
    populate_tables()
    popup.destroy()

# Create Process Popup
def create_process_popup():
    popup = tk.Toplevel()
    popup.title("Create New Process")
    popup.geometry("400x500")
    
    labels = ["Process ID", "Burst Time", "Priority", "Remaining Time", "CPU", "Memory", "Program Counter", "Open Files", "AX", "BX"]
    entries = {}
    for i, label in enumerate(labels):
        tk.Label(popup, text=label).grid(row=i, column=0, padx=10, pady=5)
        entry = tk.Entry(popup)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[label] = entry

    tk.Button(
        popup, text="Add Process",
        command=lambda: add_process(
            popup,
            entries["Process ID"].get(),
            entries["Burst Time"].get(),
            entries["Priority"].get(),
            entries["Remaining Time"].get(),
            entries["CPU"].get(),
            entries["Memory"].get(),
            entries["Program Counter"].get(),
            entries["Open Files"].get(),
            entries["AX"].get(),
            entries["BX"].get()
        )
    ).grid(row=len(labels), column=0, columnspan=2, pady=10)

# GUI Components Initialization
root = tk.Tk()
root.title("OS Simulator with PCB")
root.geometry("1200x800")

small_font = ("Arial", 8)

# Top Block
top_block = ttk.Frame(root, width=1200)
top_block.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

running_processes_table = ttk.Treeview(top_block, columns=("Pid", "State", "Priority", "Burst", "RemainingTime"), height=5)
for col in running_processes_table["columns"]:
    running_processes_table.heading(col, text=col)
running_processes_table['show'] = 'headings'
running_processes_table.grid(row=0, column=0, padx=10, pady=5, sticky="w")

ready_queue_table = ttk.Treeview(top_block, columns=("Pid", "State", "Priority", "Burst", "RemainingTime"), height=5)
for col in ready_queue_table["columns"]:
    ready_queue_table.heading(col, text=col)
ready_queue_table['show'] = 'headings'
ready_queue_table.grid(row=1, column=0, padx=10, pady=5, sticky="w")

waiting_processes_table = ttk.Treeview(top_block, columns=("Pid", "State", "Priority", "Burst", "RemainingTime"), height=5)
for col in waiting_processes_table["columns"]:
    waiting_processes_table.heading(col, text=col)
waiting_processes_table['show'] = 'headings'
waiting_processes_table.grid(row=2, column=0, padx=10, pady=5, sticky="w")

bottom_block = ttk.Frame(root, width=1200)
bottom_block.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

pcb_frame = ttk.LabelFrame(bottom_block, text="Process Control Block (PCB)", width=300)
pcb_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nw")

pcb_labels = {
    "Program Counter": tk.StringVar(value="N/A"),
    "Number of Open Files": tk.StringVar(value="N/A"),
    "AX": tk.StringVar(value="N/A"),
    "BX": tk.StringVar(value="N/A"),
}

for i, (label_text, var) in enumerate(pcb_labels.items()):
    tk.Label(pcb_frame, text=label_text + ":", font=small_font).grid(row=i, column=0, sticky="w", padx=5, pady=2)
    tk.Label(pcb_frame, textvariable=var, font=small_font).grid(row=i, column=1, sticky="w", padx=5, pady=2)

scheduler_frame = ttk.LabelFrame(bottom_block, text="Scheduler Policies")
scheduler_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nw")

scheduler_var = tk.StringVar(value="Round Robin (RR)")
policies = ["First-Come, First-Served (FCFS)", "Round Robin (RR)"]
for policy in policies:
    tk.Radiobutton(scheduler_frame, text=policy, variable=scheduler_var, value=policy).pack(anchor=tk.W)

os_control_frame = ttk.LabelFrame(bottom_block, text="OS Control")
os_control_frame.grid(row=0, column=2, padx=10, pady=5, sticky="nw")

start_button = tk.Button(os_control_frame, text="Start", width=15, command=start_os)
start_button.pack(padx=5, pady=5)

suspend_button = tk.Button(os_control_frame, text="Suspend", width=15)
suspend_button.pack(padx=5, pady=5)

next_clock_button = tk.Button(os_control_frame, text="Next Clock", width=15, command=next_clock_cycle)
next_clock_button.pack(padx=5, pady=5)

program_list_frame = ttk.LabelFrame(bottom_block, text="Program List")
program_list_frame.grid(row=0, column=3, padx=10, pady=5, sticky="nw")

program_list_table = ttk.Treeview(program_list_frame, columns=("ProcessID", "Waiting Time", "Turnaround Time"), height=5)
program_list_table.heading("ProcessID", text="Process ID")
program_list_table.heading("Waiting Time", text="Waiting Time")
program_list_table.heading("Turnaround Time", text="Turnaround Time")
program_list_table['show'] = 'headings'
program_list_table.pack(pady=5)

average_waiting_time_label = tk.Label(program_list_frame, text="Avg Waiting Time: 0", font=small_font)
average_waiting_time_label.pack()

average_turnaround_time_label = tk.Label(program_list_frame, text="Avg Turnaround Time: 0", font=small_font)
average_turnaround_time_label.pack()

create_process_button = tk.Button(root, text="Create Process", width=15, font=small_font, command=create_process_popup)
create_process_button.pack(side=tk.BOTTOM, anchor=tk.SE, padx=20, pady=10)

root.mainloop()
