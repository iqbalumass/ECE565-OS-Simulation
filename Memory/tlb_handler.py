import tkinter as tk
from tkinter import messagebox
from Memory.memoryManagement import AddressTranslationGUI

class TLB:

    def __init__(self):
         #initialize tlb table

        self.tlb_table = {
                          
            10: (31, 1, "RW"),  # Virtual Page -> (Physical Page, Modified, Protection)
            3: (3, 1, "RW"),
            13: (29, 1, "RW"),
            12: (62, 1, "RW"),
            1: (1, 1, "RW"),
            21: (45, 0, "R"),
            60: (14, 1, "RW"),
            61: (75, 1, "RW"),
        }

        self.hit_count = 0
        self.miss_count = 0



    def getMemory(self, virtual_address):
            """Translate a virtual address to a physical address using the TLB."""
            virtual_page = virtual_address // 16  # Upper 4 bits
            offset = virtual_address % 16        # Lower 4 bits

            if virtual_page in self.tlb_table:
                # TLB Hit
                physical_page, _, _ = self.tlb_table[virtual_page]
                self.hit_count += 1

                physical_address = physical_page * 16 + offset  # Calculate PA

                self.show_message(f"TLB Hit! Virtual Address {virtual_address} maps to Physical Address {physical_address}")
                return physical_address
            
            else:
                # TLB Miss
                self.miss_count += 1
                # messagebox.showwarning("TLB Miss", f"Page {virtual_page} not found in TLB.")
                # address_translation_gui = AddressTranslationGUI(None)  # Instantiating with None (or you can pass a root object if needed)
            # return address_translation_gui.translateVirtualAddress(virtual_address)
            return None
    
    def show_message(self, message):
        """Show a popup message."""
        root = tk.Tk()  # Create a root window
        root.withdraw()  # Hide the root window (we only want the popup)
        messagebox.showinfo("Address Translation", message)  # Show the message box
        root.destroy()  # Close the root window after the message
            
    def get_statistics(self):
        """
        Return the current hit and miss counts.
        """
        return {"hit_count": self.hit_count, "miss_count": self.miss_count}
        
        
