from abc import ABC, abstractmethod

class BLOCK:
    def __init__(self):
        self.files = None

class BlockGUI(ABC): 
    @abstractmethod
    def __init__(self):
        """
        Initialize GUI-specific settings for the allocation type.
        """
        pass

    @abstractmethod
    def load_entries(self):
        """
        Load the block entries into the GUI for visualization.
        """
        pass

    @abstractmethod
    def update_block_label(self, block_index, label):
        """
        Update the label of a block on the GUI.
        :param block_index: The block to update.
        :param label: The new label to display.
        """
        pass

    @abstractmethod
    def update_read_write_label(self, label):
        """
        Update the read/write label in the GUI.
        """
        pass

    @abstractmethod
    def update_file(self, file_name, operation):
        """
        Update the GUI for a specific file operation.
        :param file_name: Name of the file.
        :param operation: "add" or "remove".
        """
        pass