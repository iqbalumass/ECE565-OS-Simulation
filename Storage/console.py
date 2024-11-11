import json

# Initialize global variables for disk blocks and block count
total_blocks = 32
disk_blocks = [None] * total_blocks
reads=0
writes=0

def load_disk_blocks(file_path):
    global disk_blocks
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Fill the disk blocks based on each file's start and length
    for item in data:
        file_name = item['file']
        start = item['start']
        length = item['length']
        
        # Mark each block for the current file
        for i in range(start, start + length):
            if i < total_blocks:
                disk_blocks[i] = file_name
    
    # Display initial block state
    display_disk_blocks()

def display_disk_blocks(highlight_index=None):
    """Print the status of the entire disk blocks, highlighting the newly added block."""
    
    print("Disk Block Information:")
    for i, block in enumerate(disk_blocks):
        # Prepare the block info, highlighting if it matches the highlight index
        block_info = f"[*{block if block else 'Empty'}*]" if highlight_index == i else f"{block if block else 'Empty'}"
        
        # Print each block, 8 blocks per row
        print(f"Block {i}: {block_info}", end="\t")
        
        # Move to a new line after every 8 blocks
        if (i + 1) % 8 == 0:
            print()  # Newline after every 8 blocks
    print()  # Extra newline at the end for separation


def add(file_name, start, length, position, reads, writes):
    global disk_blocks
    highlight_index = None  # Default: no block highlighted
    
    # Check for adding at the "beginning"
    if position == "beginning":
        
        if start - 1 > 0 and disk_blocks[start - 1] is None:
            print('Add block to beginning without shifting')
            disk_blocks[start - 1] = file_name
            highlight_index = start - 1  # Highlight this block
            writes=writes+1
            print(writes)
        elif start-1>=0 and disk_blocks[start - 1]is not None:
            print('Add block to beginning with shifting')
            if start + length < total_blocks and disk_blocks[start + length] is None:
                for i in range(total_blocks - 1, start, -1):
                    disk_blocks[i] = disk_blocks[i - 1] if i > start else None
                    reads=reads+1
                    writes=writes+1
                highlight_index = start  # Highlight the added block at start
            writes=writes+1
        elif start-1<0:
            print('Add block to beginning with shifting')
            if start + length < total_blocks and disk_blocks[start + length] is None:
                for i in range(start+length, start, -1):
                    disk_blocks[i] = disk_blocks[i - 1] if i > start else None
                    reads=reads+1
                    writes=writes+1
                highlight_index = start  # Highlight the added block at start
            writes=writes+1

        else:
            print('No space')
        print(f"Read:{reads} and Writes:{writes}")
    # Check for adding at the "middle"
    elif position == "middle":
        print("there will always be shifting if there is space-middle case")
        print('\\\\\original length of odd and even case for middle needs to be handled\\\\\\ ')
        
        if start == 0:
            target = start + (length // 2)
        elif start!=0 and start+length==32:
            target = start + (length // 2) - 1
        else:
            target=start + (length // 2) 

        ### case count: if length is 2, 2//2=1. if length is 3, 3//2=1  && case f: if if length=2, 2//2=1. if  length=3, 3//2=1 &&& case list= length=4//2=2
        print(target) ### case count: if start=0, target becomes 0+1=1    && case f: if start=6, target becomes 6+1=7 && case list, if start=28, target id 28+2=30
        print(f'We have to move block item from target block {target}')
        print(f'Making it a list as we can shift eitheri left or right')
        num_of_blocks_to_move=[length//2, (length//2)+1] #if file length is even, we move length//2 blocks, else we move length//2+1 blocks

        '''
        Case 1: There is space to the right. i.e. disk_block[start+length] is None.. for count, disk_block[0+2]=2, for f,disk_block[6+2]=8, for list, disk_block[28+4]=32
        Case 2: There is space to the left, i.e., disk_block[start-1] is None.. for count, disk_block[0-1]=-1 for disk_block[6-1]=5 and for list, disk_blocl[28-1]=27
        Case 3: No space at all        
        '''
        if start==0:
            '''
            we try and see if Case 1 applies
            '''
            if disk_blocks[start + length]==None:
                print(f'Block {start + length} is unallocated')
                print('shift right')
                if length%2==0:
                    print(f'moving {num_of_blocks_to_move[0]} blocks')
                    print(f"Target is start+(length//2)")
                    for i in range(start+length,target,-1):
                        print(f'moving block {i-1} to block {i}')
                        disk_blocks[i]=disk_blocks[i-1]
                        disk_blocks[i-1]=None
                        reads=reads+1
                        writes=writes+1
                    print('Allocation space made, now insert at target') 
                    print(f'disk block {target} has {disk_blocks[target]}')  
                    disk_blocks[target]=file_name
                    writes=writes+1
                    print(f'disk block {target} has {disk_blocks[target]}')
                else:
                    print(f'moving {num_of_blocks_to_move[1]} blocks')
                    print(f"Target is start+(length//2)")
                    for i in range(start+length,target,-1):
                        print(f'moving block {i-1} to block {i}')
                        disk_blocks[i]=disk_blocks[i-1]
                        disk_blocks[i-1]=None
                        reads=reads+1
                        writes=writes+1
                    print('Allocation space made, now insert at target')   
                    print(f'disk block {target} has {disk_blocks[target]}')
                    disk_blocks[target]=file_name
                    print(f'disk block {target} has {disk_blocks[target]}')

        elif start+length==32:
            '''
            we try and see if Case 2 applies
            ''' 
            if disk_blocks[start-1]==None:
                print(f'Block {start-1} is unallocated')
                print('shift left')
                if length%2==0:
                    print(f'moving {num_of_blocks_to_move[0]} blocks')
                    print(f"Target is start+(length//2)")
                    for i in range(start-1,target,1):
                        print(f'moving block {i+1} to block {i}')
                        disk_blocks[i]=disk_blocks[i+1]
                        disk_blocks[i+1]=None
                        reads=reads+1
                        writes=writes+1
                    print('Allocation space made, now insert at target') 
                    print(f'disk block {target} has {disk_blocks[target]}')  
                    disk_blocks[target]=file_name
                    writes=writes+1
                    print(f'disk block {target} has {disk_blocks[target]}')

                else:
                    print(f'moving {num_of_blocks_to_move[1]} blocks')
                    print(f"Target is start+(length//2)")
                    for i in range(start-1,target,1):
                        print(f'moving block {i+1} to block {i}')
                        disk_blocks[i]=disk_blocks[i+1]
                        disk_blocks[i+1]=None
                        reads=reads+1
                        writes=writes+1
                    print('Allocation space made, now insert at target') 
                    print(f'disk block {target} has {disk_blocks[target]}')  
                    disk_blocks[target]=file_name
                    print(f'disk block {target} has {disk_blocks[target]}')
        else:
            '''
            start>0 and start+length<32, prefer to apply Case 1 than Case 2
            '''
            if disk_blocks[start + length]==None:
                print(f'Block {start + length} is unallocated')
                print('shift right')
                print(f'target is {target}')
                if length%2==0:
                    print(f'moving {num_of_blocks_to_move[0]} blocks')
                    print(f"Target is start+(length//2)")
                    for i in range(start+length,target,-1):
                        print(f'moving block {i-1} to block {i}')
                        disk_blocks[i]=disk_blocks[i-1]
                        disk_blocks[i-1]=None
                        reads=reads+1
                        writes=writes+1
                    print('Allocation space made, now insert at target') 
                    print(f'disk block {target} has {disk_blocks[target]}')  
                    disk_blocks[target]=file_name
                    writes=writes+1
                    print(f'disk block {target} has {disk_blocks[target]}')

                else:
                    print(f'moving {num_of_blocks_to_move[1]} blocks')
                    print(f"Target is start+(length//2)")
                    for i in range(start+length,target,-1):
                        print(f'moving block {i-1} to block {i}')
                        disk_blocks[i]=disk_blocks[i-1]
                        disk_blocks[i-1]=None
                        reads=reads+1
                        writes=writes+1
                    print('Allocation space made, now insert at target')   
                    print(f'disk block {target} has {disk_blocks[target]}')
                    disk_blocks[target]=file_name
                    print(f'disk block {target} has {disk_blocks[target]}')

            
            elif disk_blocks[start - 1]==None:
                print(f'Block {start-1} is unallocated')
                print('shift left')

                if length%2==0:
                    print(f'moving {num_of_blocks_to_move[0]} blocks')
                    print(f"Target is start+(length//2)")
                    for i in range(start-1,target,1):
                        print(f'moving block {i+1} to block {i}')
                        disk_blocks[i]=disk_blocks[i+1]
                        disk_blocks[i+1]=None
                        reads=reads+1
                        writes=writes+1
                    print('Allocation space made, now insert at target') 
                    print(f'disk block {target} has {disk_blocks[target]}')  
                    disk_blocks[target]=file_name
                    print(f'disk block {target} has {disk_blocks[target]}')
                else:
                    print(f'moving {num_of_blocks_to_move[1]} blocks')
                    print(f"Target is start+(length//2)")
                    for i in range(start-1,target,1):
                        print(f'moving block {i+1} to block {i}')
                        disk_blocks[i]=disk_blocks[i+1]
                        disk_blocks[i+1]=None
                        reads=reads+1
                        writes=writes+1
                    print('Allocation space made, now insert at target') 
                    print(f'disk block {target} has {disk_blocks[target]}')  
                    disk_blocks[target]=file_name
                    print(f'disk block {target} has {disk_blocks[target]}')

            else:
                print('NO SPACE')

        print(f"Read:{reads} and Writes:{writes}")
        highlight_index=target
    
    # Check for adding at the "end"
    elif position == "end":
        
        if start + length < total_blocks and disk_blocks[start + length] is None :
            print('Add block to ending need no shifting')
            disk_blocks[start + length] = file_name
            highlight_index = start + length  # Highlight the added block
            writes=writes+1
        elif start - 1 > 0 and disk_blocks[start - 1] is None:
            print('Add block to ending needs shifting')
            for i in range(start+length - 1, start - 1, -1):
                print(f'move block {i} to {i-1}')
                disk_blocks[i] = disk_blocks[i - 1] if i > start else None
                reads=reads+1
                writes=writes+1
            disk_blocks[start-1] = file_name
            writes=writes+1
            highlight_index = start+length  # Highlight the added block at end position
        else:
            print('NO SPACE')
        print(f"Read:{reads} and Writes:{writes}")
            
    
    # Display the updated disk blocks with the new block highlighted
    print(f"Added block for file '{file_name}' at position '{position}' at block .")
    display_disk_blocks(highlight_index)
    return True

def remove(file_name,start,length, position, reads, writes):
    if position=='beginning':
        print(f'remove block at {start}')
        disk_blocks[start]=None
        highlight_index=start
        for i in range(start, start+length-1,1):
            print(f'move block {i+1} to {i}')
            disk_blocks[i]=disk_blocks[i+1]
            disk_blocks[i+1]=None
            reads=reads+1
            writes=writes+1
        disk_blocks[start + length-1]=None
        print(f'block {start+length} is now {disk_blocks[start + length-1]}')
    elif position=='middle':
        print(f'remove block at {start+(length//2)}') 
        '''
        After removing we gotta move the blocks.   '''
        target=start+(length//2)
        disk_blocks[target]=None
        for i in range(target, start+length-1,1):
            print(f'move block {i+1} to {i}')
            disk_blocks[i]=disk_blocks[i+1]
            disk_blocks[i+1]=None
            reads=reads+1
            writes=writes+1
        disk_blocks[start + length-1]=None
        print(f'block {start+length-1} is now {disk_blocks[start + length-1]}')
        #writes=writes+1
        highlight_index=target
    else: #position=end
        print(f'remove block at {start+length-1}')
        disk_blocks[start + length-1]=None
        highlight_index=start+length-1
    length=length-1
    display_disk_blocks(highlight_index)
    print(f'Reads:{reads}, Writes: {writes}' )

# Usage
load_disk_blocks('directory.json')
#add('count', 0, 2, 'beginning', reads, writes)  # Adding a block at the beginning
#add('count', 0, 2, 'end', reads, writes)  # Adding a block at the end
#add('count', 0, 3, 'middle', reads, writes)  # Adding a block in the middle
#add('list',27,5,'middle', reads, writes)
#add('f',6,2,'middle', reads, writes)
#remove('count', 0, 2, 'beginning', reads, writes)
#remove('count', 0, 2, 'middle', reads, writes)
#remove('list',28,4,'middle', reads, writes)
#remove('count', 0, 2, 'end', reads, writes)
#remove('list',28,4,'end', reads, writes)


'''
Test cases on list: Please check
'''
#add('list',28,4,'beginning', reads, writes) #Ans: reads=0, writes=1
#add('list',28,4,'middle', reads, writes) #Ans: reads=2, writes=3
#add('list',28,4,'end', reads, writes) #Ans: reads=4 ,writes=5
#remove('list',28,4,'beginning', reads, writes) #Ans: reads=3,writes=3
#remove('list',28,4,'middle', reads, writes) #Ans:reads=2, writes=2 or reads=1, writes=1
#remove('list',28,4,'end', reads, writes) #Ans: reads=0,writes=0

'''
Test case on count: Please check
'''
#add('count', 0, 2, 'beginning', reads, writes)# Ans: read=2, writes=3
#add('count', 0, 2, 'middle', reads, writes)   #Ans: read= 1, writes=2
#add('count', 0, 2, 'end', reads, writes) # Ans: read=0, writes=1
#remove('count', 0, 2, 'beginning', reads, writes)# Ans: reads=1,writes=1
#remove('count', 0, 2, 'middle', reads, writes)  #Ans: reads=1, writes=1
#remove('count', 0, 2, 'end', reads, writes) #Ans: reads=0 , writes=0



'''
Test case on f: Please check
'''
#add('f', 6, 2, 'beginning', reads, writes)# Ans: read=0, writes=1
#add('f', 6, 2, 'middle', reads, writes)   #Ans: read= 1, writes=2
#add('f', 6, 2, 'end', reads, writes) # Ans: read=0, writes=1
#remove('f', 6, 2, 'beginning', reads, writes)# Ans: reads=1,writes=1
#remove('f', 6, 2, 'middle', reads, writes)  #Ans: reads=1, writes=1
#remove('f', 6, 2, 'end', reads, writes) #Ans: reads=0 , writes=0

# To print the entire disk block status:
#display_disk_blocks()
