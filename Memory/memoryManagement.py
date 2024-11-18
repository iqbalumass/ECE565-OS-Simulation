import tkinter as tk
from tkinter import ttk, messagebox
import random

class AddressTranslationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual to Physical Address Translation")
        self.address_pool = []  # Store generated addresses
        self.fifo_queue = []    # FIFO queue for frames
        self.max_frames = 4     # Maximum frames in FIFO

        # Address Pool
        tk.Label(root, text="Address Pool", font=("Arial", 14)).grid(row=0, column=0, sticky="w")
        self.address_pool_listbox = tk.Listbox(root, height=10)
        self.address_pool_listbox.grid(row=1, column=0, padx=5, pady=5)

        # Virtual Address Table
        tk.Label(root, text="Virtual Address Table", font=("Arial", 14)).grid(row=0, column=1, sticky="w")
        self.virtual_table = ttk.Treeview(root, columns=("Frame", "Offset"), show="headings", height=10)
        self.virtual_table.heading("Frame", text="Frame Number")
        self.virtual_table.heading("Offset", text="Offset")
        self.virtual_table.grid(row=1, column=1, padx=5, pady=5)

        # Page Table
        tk.Label(root, text="Page Table", font=("Arial", 14)).grid(row=0, column=2, sticky="w")
        self.page_table = ttk.Treeview(root, columns=("Frame", "Valid"), show="headings", height=10)
        self.page_table.heading("Frame", text="Frame Number")
        self.page_table.heading("Valid", text="Valid Bit")
        self.page_table.grid(row=1, column=2, padx=5, pady=5)

        # FIFO Queue
        tk.Label(root, text="FIFO Queue", font=("Arial", 14)).grid(row=0, column=3, sticky="w")
        self.fifo_queue_listbox = tk.Listbox(root, height=10)
        self.fifo_queue_listbox.grid(row=1, column=3, padx=5, pady=5)

        # Physical Address Space
        tk.Label(root, text="Physical Address Space", font=("Arial", 14)).grid(row=0, column=4, sticky="w")
        self.physical_table = ttk.Treeview(root, columns=("Address"), show="headings", height=10)
        self.physical_table.heading("Address", text="Memory Address")
        self.physical_table.grid(row=1, column=4, padx=5, pady=5)

        # Buttons to control address generation and translation
        tk.Button(root, text="Generate Virtual Address", command=self.generate_virtual_address).grid(row=2, column=0, pady=10)
        tk.Button(root, text="Translate to Physical Address", command=self.translate_address).grid(row=2, column=1, pady=10)

    def generate_virtual_address(self):
        # Generate a random virtual address
        virtual_address = random.randint(0, 1023)  # Example address within a range
        self.address_pool.append(virtual_address)
        self.address_pool_listbox.insert(tk.END, f"Virtual Address: {virtual_address}")
        
        # Calculate frame and offset as example (modify with actual logic)
        frame = virtual_address // 64
        offset = virtual_address % 64
        self.virtual_table.insert("", tk.END, values=(frame, offset))

    def update_fifo_queue(self, frame, physical_address):
        # Add frame to FIFO queue and update the listbox
        if frame not in self.fifo_queue:
            if len(self.fifo_queue) >= self.max_frames:
                # Remove the oldest frame if max size is reached
                removed_frame = self.fifo_queue.pop(0)
                self.update_physical_address_space(removed_frame, remove=True)
            self.fifo_queue.append(frame)
            self.fifo_queue_listbox.insert(tk.END, f"Frame {frame} - Address {physical_address}")

    def update_physical_address_space(self, frame, physical_address=None, remove=False):
        # Update the Physical Address Space table
        if remove:
            # Remove the frame from the physical address space
            items = self.physical_table.get_children()
            for item in items:
                if self.physical_table.item(item, "values")[0] == f"Frame {frame}":
                    self.physical_table.delete(item)
                    break
        else:
            # Add frame with its physical address to the physical address space
            self.physical_table.insert("", tk.END, values=(f"Frame {frame} - Address {physical_address}"))

    def translate_address(self):
        # Check if an address is selected in the Address Pool
        selected_index = self.address_pool_listbox.curselection()
        if selected_index:
            # Get the selected virtual address
            virtual_address = self.address_pool[selected_index[0]]
            
            # Example translation logic (replace with your actual logic)
            frame = virtual_address // 64  # Frame number calculation
            offset = virtual_address % 64  # Offset within the frame
            physical_address = frame * 64 + offset  # Physical address calculation

            # Update the Page Table with frame and validity
            self.page_table.insert("", tk.END, values=(frame, "Valid" if frame < 4 else "Invalid"))
            
            # Update FIFO Queue and Physical Address Space
            self.update_fifo_queue(frame, physical_address)
            self.update_physical_address_space(frame, physical_address)

            # Show a message indicating the translated physical address
            messagebox.showinfo("Translation", f"Virtual Address {virtual_address} translated to Physical Address {physical_address}")
        else:
            messagebox.showwarning("Warning", "Please select a virtual address from the Address Pool to translate.")

root = tk.Tk()
app = AddressTranslationGUI(root)
root.mainloop()
