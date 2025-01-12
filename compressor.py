import heapq # to make the first element is the smallest one
import os
import pickle  # To save the frequency table (or tree)
import customtkinter
from tkinter import filedialog

def compress(input_file):
    with open(input_file, 'rb') as file:
        data = file.read()
        
    # Step 1: Calculate frequency of each character
        freq_dict = {}
        for byte in data:
            freq_dict[byte] = freq_dict.get(byte, 0) + 1

    # Step 2: Build a heap of binary tree nodes
    heap = []
    for key, freq in freq_dict.items():
        heapq.heappush(heap, (freq, key))
    counter = 0

    # Step 3: Build the Huffman binary tree
    while len(heap) > 1:
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        counter += 1
        new_node = (node1[0] + node2[0], counter, node1, node2)  # Add a counter because an error
        heapq.heappush(heap, new_node)

    root = heapq.heappop(heap)

    # Generate Huffman codes
    def generate_codes(node, prefix, codes):
        if len(node) == 2:  # Leaf node
            codes[node[1]] = prefix
            return
        generate_codes(node[2], prefix + '0', codes)  # Left child
        generate_codes(node[3], prefix + '1', codes)  # Right child

    codes = {}
    generate_codes(root, '', codes)

    # Encode the text
    encoded_data = ''.join(codes[byte] for byte in data)

    # Padding to make the encoded text a multiple of 8 bits
    padding = 8 - len(encoded_data) % 8 if len(encoded_data) % 8 != 0 else 0
    encoded_data = '0' * padding + encoded_data  # Add leading zeros as padding

    # Write compressed data to file
    base_name, _ = os.path.splitext(input_file)
    metadata = {"codes":codes,"ext":_}
    with open(base_name+"Metadata_file.json",'wb') as file:
        pickle.dump(metadata, file)

    with open(f"{base_name}.bin", 'wb') as file:
        file.write(padding.to_bytes(1, 'big'))  # Save the padding length
        file.write(int(encoded_data, 2).to_bytes((len(encoded_data) + 7) // 8, 'big'))

    return f"{base_name}.bin"

def decompress(file_path):
    base_name, _ = os.path.splitext(file_path)

    # Load the codes from the metadata file
    with open(base_name + "Metadata_file.json", "rb") as file:
        metadata = pickle.load(file)
    codes = metadata['codes']
    ext = metadata['ext']
    # Reverse the codes dictionary for decoding
    reverse_codes = {v: k for k, v in codes.items()}

    # Read the compressed binary file
    with open(file_path, 'rb') as file:
        padding = int.from_bytes(file.read(1), 'big')  # First byte is the padding
        encoded_data = file.read()
        binary_string = bin(int.from_bytes(encoded_data, 'big'))[2:]  # Convert bytes to binary string
        binary_string = binary_string.zfill(len(encoded_data) * 8)  # Ensure full binary representation
        binary_string = binary_string[padding:]  # Remove the padding bits

    # Decode the binary string using the reverse codes
    current_code = ""
    decoded_data = bytearray()  # Use bytearray for binary data
    for bit in binary_string:
        current_code += bit
        if current_code in reverse_codes:
            decoded_data.append(reverse_codes[current_code])
            current_code = ""

    # Write the decompressed data to a file
    output_file = base_name+"_decompressed" + ext
    with open(output_file, "wb") as file:
        file.write(decoded_data)

    return output_file

# enable area to write message then close it
def update_text_area(message):
    text_area.configure(state='normal') 
    text_area.insert('end', message + '\n'+"-"*30 +'\n')  
    text_area.configure(state='disabled')  

# select the compressed file with the filedialog
def select_file():
    file_paths = filedialog.askopenfilenames(title="Select Files", filetypes=[("All Files", "*.*")])
    if file_paths:
        for file in file_paths:
            try:
                output = compress(file)
                update_text_area(f"File compressed successfully!\nOutput file: {output}")
            except Exception as e:
                update_text_area(f"File compressed Failed!/Error file: {file}")
            

# select the decompressed file with the filedialog
def select_decompress_file():
    file_paths = filedialog.askopenfilenames(title="Select Compressed Files", filetypes=[("Compressed Files", "*.bin")])
    if file_paths:
        for file in file_paths:
            try:
                output = decompress(file)
                update_text_area(f"File decompressed successfully!\nOutput file: {output}")
            except Exception as e:
                update_text_area(f"File decompressed Failed!/Check MetaData For: {file} ")
            

# Create the main application window
app = customtkinter.CTk()
app.title("File Compression Utility")
app.geometry("400x300")


# Create buttons for compression and decompression
compress_button = customtkinter.CTkButton(app, text="Compress File", command=select_file)
compress_button.grid(row=0, column=0, padx=10, pady=10)  

decompress_button = customtkinter.CTkButton(app, text="Decompress File", command=select_decompress_file)
decompress_button.grid(row=0, column=1, padx=10, pady=10)  

# Create a text area
text_area = customtkinter.CTkTextbox(app, width=380, height=200, state='disabled',wrap='none')
text_area.grid(row=1, column=0, columnspan=2, padx=10, pady=10)  


app.mainloop()
