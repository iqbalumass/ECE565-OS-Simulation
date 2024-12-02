# test_script.py

import sys
import os
from tkinter import Tk

# Add the project root directory to sys.path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Memory.tlb_handler import TLB, display_tlb_table    # Import TLB class from Memory/tlb_handler.py
from Memory.memoryManagement import AddressTranslationGUI  # Import AddressTranslationGUI from Memory/memoryManagement.py

def test_tlb_with_virtual_address():
    # Create an instance of the TLB class
    tlb = TLB()

    # Example virtual address for testing
    virtual_address = 193  # Change this virtual address to test different cases

    print(f"Testing with Virtual Address: {virtual_address}")

    # Call getMemory() from TLB class which will check if TLB has the entry
    physical_address = tlb.getMemory(virtual_address)

    if physical_address is not None:
        print(f"Physical Address for Virtual Address {virtual_address}: {physical_address}")
    else:
        print(f"TLB Miss: Translation failed for Virtual Address {virtual_address}")

    # Launch the TLB table GUI
    root = Tk()
    display_tlb_table(root, tlb)
    root.mainloop()

# Run the test case
test_tlb_with_virtual_address()
