import os
import subprocess


def main():
    # Ask the user for the file to upload
    input_file = input("Please enter the file you want to upload: ")

    # Validate input file
    if not os.path.exists(input_file):
        print(f"The file {input_file} does not exist. Exiting...")
        return

    # Ask the user for the output file name
    output_file = input("Please enter the output file name (e.g., 'output.jpg'): ")

    # Validate output file name (check if file exists)
    if os.path.exists(output_file):
        print(f"The file {output_file} already exists. Exiting...")
        return

    # Start network simulator
    simulator_process = subprocess.Popen(["python", "network_simulator.py"])

    # Start receiver with the output file as an argument
    receiver_process = subprocess.Popen(["python", "receiver.py", output_file])

    # Start sender with the input file as an argument
    sender_process = subprocess.Popen(["python", "sender.py", input_file])

    # Wait for processes to complete
    sender_process.wait()
    receiver_process.wait()
    simulator_process.terminate()

    print("File transfer complete.")


if __name__ == "__main__":
    main()
