# Reliable File Transfer System

This project implements a reliable file transfer protocol using UDP with features such as acknowledgments, retransmissions, timeouts, and packet reordering. It consists of a sender, receiver, and a network simulator that introduces loss, corruption, and reordering for testing.

## Requirements
- Python 3.x

## File Descriptions
- `sender.py` - Sends a file to the receiver in chunks, implementing reliability mechanisms.
- `receiver.py` - Receives packets, handles reordering, and writes the received file to disk.
- `network_simulator.py` - Simulates packet loss, corruption, and reordering.
- `utils.py` - Contains helper functions and constants for packet handling.
- `launcher.py` - Automates the process of starting all components.

## How to Run

### Running with `launcher.py` (Recommended)
To automatically start all components, run:
```sh
python launcher.py
```
Follow the prompts to specify the input file and output file.

### Running Manually
#### Step 1: Start the Network Simulator
```sh
python network_simulator.py
```

#### Step 2: Start the Receiver
```sh
python receiver.py output_file
```
Replace `output_file` with the name of the file to be saved.

#### Step 3: Start the Sender
```sh
python sender.py input_file
```
Replace `input_file` with the file you want to send.

## Example Usage
### Example 1: Using the Launcher
```sh
python launcher.py
```
- Input file: `example.txt`
- Output file: `received_example.txt`

### Example 2: Running Manually
```sh
python network_simulator.py &
python receiver.py received_image.jpg &
python sender.py image.jpg
```

This will transfer `image.jpg` to `received_image.jpg` via the simulated network.

## Notes
- The network simulator introduces packet loss, corruption, and reordering for testing reliability.
- Ensure that all components are running before starting the sender.
- The receiver will reconstruct the file and write it to disk after receiving all packets.

