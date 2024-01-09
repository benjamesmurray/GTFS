# GTFS
Tools for interacting with the BODS GTFS feed. 


# How to Run the Files

This repository contains Python files that depend on Protocol Buffers. Follow these steps to set up and run the files:

# Prerequisites

- **Git**: Install Git to clone the repository. Download it from [git-scm.com](https://git-scm.com/).
- **Python**: Required to run the files. Download from [python.org](https://www.python.org/).
- **Protocol Buffers Compiler (protoc)**: Required to compile `.proto` files.

# Steps

1. **Clone the Repository**:
   ```
   git clone [URL of the repository]
   ```
   Replace `[URL of the repository]` with the URL of this GitHub repository.

2. **Navigate to the Repository Directory**:
   ```
   cd [Name of the repository]
   ```
   Replace `[Name of the repository]` with the directory name of the cloned repository.

3. **Install Required Python Packages** (if applicable):
   If there's a `requirements.txt` file, install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

4. **Install Protocol Buffers Compiler (protoc)**:
   - Download `protoc` from the [Protocol Buffers GitHub page](https://github.com/protocolbuffers/protobuf).
   - Choose the appropriate version for your operating system.
   - Extract the downloaded file and note the path to the `protoc` executable.

5. **Add `protoc` to Your System's PATH**:
   - **Windows**:
     - Right-click on 'This PC' or 'Computer' on your desktop or in File Explorer, then choose 'Properties'.
     - Click on 'Advanced system settings' -> 'Environment Variables'.
     - Under 'System variables', find and select 'Path', then click 'Edit'.
     - Click 'New' and add the path to the folder where `protoc` is located.
     - Click 'OK' to close all dialog boxes.
   - **macOS/Linux**:
     - Open your terminal.
     - Run `export PATH=$PATH:/path/to/protoc-folder`.
     - Replace `/path/to/protoc-folder` with the actual path to the folder containing `protoc`.

6. **Set Up the Protocol Buffer (`.proto`) File**:
   - Locate the `.proto` file in the repository.
   - Compile the `.proto` file to generate Python classes:
     ```
     protoc --python_out=. your_proto_file.proto
     ```
   - Replace `your_proto_file.proto` with the path to your `.proto` file.

7. **Run the Python Files**:
   - Execute the Python scripts using:
     ```
     python filename.py
     ```
   - Replace `filename.py` with the name of the Python file you want to run.

# Additional Notes

- Ensure you are in the correct directory when executing commands.
- For additional setup or running parts of a larger application, refer to specific instructions provided in the repository.
```
