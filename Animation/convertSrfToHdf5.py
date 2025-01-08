import pandas as pd
import h5py
import numpy as np

# Function to parse SRF file content
def parse_srf_file_content(file_content):
    data_section_found = False
    topology_section_found = False
    body_ids = []
    blocks = []
    current_block = []
    block_length = 0

    # Split content into lines
    lines = file_content.strip().split('\n')

    # Process each line
    for line in lines:
        line = line.strip()

        # Identify "Topology" section
        if line == "Topology":
            topology_section_found = True
            continue

        # Identify "Data" section
        if line == "Data":
            data_section_found = True
            continue

        # Ignore lines that are not valid data
        if line.startswith("--") or not line:
            continue

        # Read body IDs in "Topology" section
        if topology_section_found:
            topology_section_found = False
            body_ids.extend(map(int, line.split()))  # Read body IDs
            block_length = 1 + len(body_ids)  # 1 (timestamp) + N (body states)
            continue

        # Skip lines until "Data" is found
        if not data_section_found:
            continue

        # Collect lines into blocks based on the dynamic block length
        current_block.append(line)
        if len(current_block) == block_length:
            # Parse block into structured data
            timestamp = float(current_block[0])  # Parse timestamp as float

            # Parse body states
            body_states = []
            for body_state_line in current_block[1:]:
                body_data = list(map(float, body_state_line.split()))
                position = body_data[:3]  # x, y, z
                rotation_flat = body_data[3:]  # Flattened 3x3 rotation matrix
                rotation_matrix = np.array(rotation_flat).reshape(3,3,order='F')
                body_states.append({"position": position, "rotation_matrix": rotation_matrix})

            # Add to blocks
            blocks.append({"timestamp": timestamp, "body_states": body_states})
            current_block = []

    return blocks, body_ids

# Example usage
file_path = 'Animation/test.srf'

with open(file_path, 'r') as file:
    file_content = file.read()

# Parse SRF file content
blocks, body_ids = parse_srf_file_content(file_content)

# Function to save parsed SRF data into an optimized HDF5 format
def save_to_hdf5(blocks, body_ids, hdf5_file):
    with h5py.File(hdf5_file, "w") as f:
        # Extract timestamps
        timestamps = np.array([block["timestamp"] for block in blocks])
        f.create_dataset("timestamps", data=timestamps, compression="gzip")
        
        # Create groups for each body
        for body_id in body_ids:
            body_group = f.create_group(f"bodyID: {body_id}")
            
            # Extract positions and rotation matrices for this body
            positions = []
            rotations = []
            for block in blocks:
                body_state = block["body_states"][body_ids.index(body_id)]
                positions.append(body_state["position"])
                rotations.append(body_state["rotation_matrix"])
            
            # Store positions and rotations as datasets
            body_group.create_dataset("positions", data=np.array(positions), compression="gzip")
            body_group.create_dataset("rotations", data=np.array(rotations), compression="gzip")

# Save data to HDF5
hdf5_file = "Animation/test.h5"
save_to_hdf5(blocks, body_ids, hdf5_file)
import h5py

# Function to read and display data from the optimized HDF5 file
def read_hdf5_file(h5Path):
    try:
        with h5py.File(h5Path, "r") as f:
            # Read timestamps
            timestamps = f["timestamps"][:]
            body_ids = [key for key in f.keys() if key.startswith("bodyID")]
            for timestep_index in range(timestamps.size):
                for body_id in body_ids:
                    print(f[f"{body_id}/positions"][timestep_index])
                    print(f[f"{body_id}/rotations"][timestep_index])

    except FileNotFoundError:
        print(f"File not found: {h5Path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Read and display the data
read_hdf5_file(hdf5_file)
