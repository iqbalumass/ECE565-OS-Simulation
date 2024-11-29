import tkinter as tk
from tkinter import ttk, messagebox
import random

class AddressTranslationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual to Physical Address Translation (8-bit)")
        self.address_pool = []  # Store generated addresses
        self.fifo_queue = []    # FIFO queue for frames
        self.max_frames = 4     # Maximum frames in FIFO

        # Address Pool
        tk.Label(root, text="Address Pool", font=("Arial", 14)).grid(row=0, column=0, sticky="w")
        self.address_pool_listbox = tk.Listbox(root, height=10)
        self.address_pool_listbox.grid(row=1, column=0, padx=5, pady=5)

        # Virtual Address Table
        tk.Label(root, text="Virtual Address Table", font=("Arial", 14)).grid(row=0, column=1, sticky="w")
        self.virtual_table = ttk.Treeview(root, columns=("Page Number", "Offset"), show="headings", height=10)
        self.virtual_table.heading("Page Number", text="Page Number")
        self.virtual_table.heading("Offset", text="Offset")
        self.virtual_table.grid(row=1, column=1, padx=5, pady=5)

        # Page Table
        tk.Label(root, text="Page Table", font=("Arial", 14)).grid(row=0, column=2, sticky="w")
        self.page_table = ttk.Treeview(root, columns=("Frame", "Status"), show="headings", height=10)
        self.page_table.heading("Frame", text="Frame Number")
        self.page_table.heading("Status", text="Status")
        self.page_table.grid(row=1, column=2, padx=5, pady=5)

        # FIFO Queue
        tk.Label(root, text="FIFO Queue", font=("Arial", 14)).grid(row=0, column=3, sticky="w")
        self.fifo_queue_listbox = tk.Listbox(root, height=10)
        self.fifo_queue_listbox.grid(row=1, column=3, padx=5, pady=5)

        # Physical Address Space
        tk.Label(root, text="Physical Address Space", font=("Arial", 14)).grid(row=0, column=4, sticky="w")
        self.physical_table = ttk.Treeview(root, columns=("Memory Address",), show="headings", height=10)
        self.physical_table.heading("Memory Address", text="Memory Address")
        self.physical_table.grid(row=1, column=4, padx=5, pady=5)

        # Add Restore from Disk Button
        tk.Button(root, text="Restore from Disk", command=self.restore_from_disk).grid(row=2, column=2, pady=10)

        # Preload Fixed Memory Addresses and Examples
        self.preload_fixed_memory_addresses()
        self.preload_examples()

    def preload_fixed_memory_addresses(self):
        # Add fixed memory address ranges
        fixed_ranges = [
            "0-15",
            "16-31",
            "32-47",
            "48-63"
        ]
        for address_range in fixed_ranges:
            self.physical_table.insert("", tk.END, values=(address_range,))

    def preload_examples(self):
        # Predefined virtual addresses with Status field included
        examples = [
            {"virtual_address": 0x34, "page_number": 3, "offset": 4, "frame_number": 3, "physical_address": 0x34, "status": "Valid"},
            {"virtual_address": 0x1A, "page_number": 1, "offset": 10, "frame_number": 1, "physical_address": 0x1A, "status": "Valid"},
            {"virtual_address": 0x7F, "page_number": 7, "offset": 15, "frame_number": 3, "physical_address": 0x3F, "status": "Valid"},
            {"virtual_address": 0x8C, "page_number": 8, "offset": 12, "frame_number": 0, "physical_address": 0x0C, "status": "Valid"},
            {"virtual_address": 0xF5, "page_number": 15, "offset": 5, "frame_number": 3, "physical_address": 0x35, "status": "Valid"},
            {"virtual_address": 0xF7, "page_number": 8, "offset": 2, "frame_number": 9, "physical_address": "-", "status": "Invalid"},
        ]

        for example in examples:
            # Add to address pool
            self.address_pool.append(example["virtual_address"])
            self.address_pool_listbox.insert(tk.END, f"Virtual Address: {example['virtual_address']}")

            # Add to virtual address table
            self.virtual_table.insert("", tk.END, values=(example["page_number"], example["offset"]))

            # Add to page table using preloaded status
            self.page_table.insert("", tk.END, values=(example["frame_number"], example["status"]))

            # Add to FIFO queue only if frame_number is valid
            if example["status"] == "Valid" and example["frame_number"] not in self.fifo_queue:
                self.fifo_queue.append(example["frame_number"])
                self.fifo_queue_listbox.insert(tk.END, f"Frame {example['frame_number']} - Address {example['physical_address']}")

    def restore_from_disk(self):
        # Get selected row from Page Table
        selected_item = self.page_table.selection()
        if selected_item:
            # Retrieve frame number from selected row
            frame_number = self.page_table.item(selected_item, "values")[0]
            print(f"Restored Frame Number: {frame_number}")
        else:
            messagebox.showwarning("No Selection", "Please select a row from the Page Table to restore.")

    def generate_virtual_address(self):
        # Generate a random 8-bit virtual address
        virtual_address = random.randint(0, 255)  # Address range for 8 bits
        self.address_pool.append(virtual_address)
        self.address_pool_listbox.insert(tk.END, f"Virtual Address: {virtual_address}")
        
        # Calculate page number and offset (8-bit logic)
        page_number = virtual_address // 16  # Upper 4 bits
        offset = virtual_address % 16        # Lower 4 bits
        self.virtual_table.insert("", tk.END, values=(page_number, offset))

    def update_fifo_queue(self, frame, physical_address):
        if frame not in self.fifo_queue:
            if len(self.fifo_queue) >= self.max_frames:
                removed_frame = self.fifo_queue.pop(0)
                self.update_physical_address_space(removed_frame, remove=True)
            self.fifo_queue.append(frame)
            self.fifo_queue_listbox.insert(tk.END, f"Frame {frame} - Address {physical_address}")

    def update_physical_address_space(self, frame, physical_address=None, remove=False):
        if remove:
            # Remove the frame from the physical address space
            items = self.physical_table.get_children()
            for item in items:
                if f"{frame * 16}-{(frame + 1) * 16 - 1}" in self.physical_table.item(item, "values")[0]:
                    self.physical_table.delete(item)
                    break
        else:
            # Add frame with its memory address range to the physical address space
            address_range_start = frame * 16
            address_range_end = address_range_start + 15
            self.physical_table.insert(
                "", 
                tk.END, 
                values=(f"{address_range_start}-{address_range_end}")
            )

root = tk.Tk()
app = AddressTranslationGUI(root)
root.mainloop()
