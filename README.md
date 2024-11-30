# ECE565 Operating Systems Simulation

Welcome to the **ECE565 Operating Systems Simulation** repository! This project is a simulation-based educational tool designed for students learning about Operating Systems (OS) concepts. The project is structured to explore key OS functionalities such as virtual memory management, process scheduling, and inter-process communication.

---

## Features

### 1. **Virtual Memory Management**
- Simulates the translation of virtual addresses to physical addresses.
- Implements page fault handling using a **FIFO page replacement algorithm**.
- Includes a random address generator (producer) to simulate virtual address generation.

### 2. **Process Scheduling**
- Simulates CPU scheduling with algorithms like **Round Robin (RR)**.
- Models process execution with predefined time quantum and state transitions.

### 3. **Inter-process Communication (IPC)**
- Uses a **producer-consumer model** for communication between processes.
- The producer generates virtual addresses, while the consumer translates them and handles page faults.

### 4. **Graphical User Interface (GUI)**
- A simple GUI built with Python for controlling simulation parameters:
  - Button to control the clock cycle (`Next Clock`).
  - Visual display of memory allocation, page faults, and process states.

---

## Installation

### Prerequisites
- Python 3.8 or higher.
- Required Python libraries (install via `pip`):
  ```bash
  pip install matplotlib tkinter numpy
