import matplotlib.pyplot as plt

# Function to read PCB information from a text file
def read_file_and_extract_pcb_info(filename):
    pcb_table = []
    pcb = []

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                # Skip comments and empty lines
                continue

            # Extract key-value pairs
            if ': ' in line:
                key, value = line.split(': ', 1)
                pcb.append(value.strip())

            # Store each process's data and reset for next process
            if key == "CPU used":
                pcb_table.append({
                    'State': pcb[0],
                    'PID': int(pcb[1]),
                    'pPID': int(pcb[2]),
                    'PC': int(pcb[3]),
                    'Burst': int(pcb[14]),
                    'Start time': pcb[15],
                    'CPU used': int(pcb[16]),
                })
                pcb = []  # Reset for the next process

    return pcb_table

def run_process_manager(pcb_table):
    global gantt_data
    gantt_data = []
    current_time = 0

    # Separate processes by their initial state
    running_processes = [pcb for pcb in pcb_table if pcb['State'] == 'Running']


    ready_processes = [pcb for pcb in pcb_table if pcb['State'] == 'Ready']
    blocked_processes = [pcb for pcb in pcb_table if pcb['State'] == 'Blocked']

    # Step 0: Run all Running processes in FIFO order
    for pcb in running_processes:
        pid = pcb['PID']
        burst_time = pcb['Burst']

        # Collect Gantt chart data
        gantt_data.append((pid, current_time, current_time + burst_time))
        current_time += burst_time

    # Step 1: Run all Ready processes in FIFO order
    for pcb in ready_processes:
        pid = pcb['PID']
        burst_time = pcb['Burst']

        # Collect Gantt chart data
        gantt_data.append((pid, current_time, current_time + burst_time))
        current_time += burst_time

    # Step 2: Run blocked processes (after all Ready processes are completed)
    for pcb in blocked_processes:
        pid = pcb['PID']
        burst_time = pcb['Burst']

        # Collect Gantt chart data
        gantt_data.append((pid, current_time, current_time + burst_time))
        current_time += burst_time

    print(f"Total time taken for all processes: {current_time} time units")


# Function to visualize Gantt chart using Matplotlib
def visualize_gantt_chart(gantt_data):

    """Visualize a Gantt chart using Matplotlib."""
    fig, ax = plt.subplots(figsize=(10, 2))  # Adjust height for a single line

    # Define colors for different processes
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']

    # Plot each process as a horizontal bar
    for i, (pid, start, end) in enumerate(gantt_data):
        ax.broken_barh([(start, end - start)], (0, 1),  # Single line at y=0
                       facecolors=colors[i % len(colors)])
        ax.text(start + (end - start) / 2, 0.5, f'PID: {pid}',  # Centered text in the middle of the bar
                ha='center', va='center', color='white', fontsize=9)

    # Configure chart labels and grid
    ax.set_xlabel('Time Units')
    ax.set_yticks([])  # Remove y ticks

    # Get end times for x-ticks and add 0
    end_times = [end for _, _, end in gantt_data]
    ticks = [0] + end_times  # Include time 0 in the ticks
    ax.set_xticks(ticks)  # Set x-ticks
    ax.set_xticklabels(ticks)  # Set labels to match ticks

    ax.grid(True)

    plt.title('Gantt Chart for Process Execution, FIFO')
    plt.show()

# Main Execution
if __name__ == "__main__":
    pcb_table = read_file_and_extract_pcb_info("ece565hw02.txt")

    run_process_manager(pcb_table)  # Generates Gantt data
    visualize_gantt_chart(gantt_data)  
