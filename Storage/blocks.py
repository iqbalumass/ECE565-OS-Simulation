import json

def print_occupied_blocks_from_file(filename):
    # Read JSON data from file
    with open(filename, 'r') as file:
        json_data = json.load(file)
    
    # Process each entry and print occupied blocks
    for entry in json_data:
        file_name = entry["file"]
        start = entry["start"]
        length = entry["length"]
        
        occupied_blocks = list(range(start, start + length))
        print(f"File '{file_name}' occupies blocks: {occupied_blocks}")

# Call the function with 'directory.json' as the filename
print_occupied_blocks_from_file('directory.json')
