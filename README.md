# GTFS
Tools for interacting with the BODS GTFS and GTFS RT data. 

**entity_counts_top3.py:** 

How many of each type of GTFS RT data is present:

Trip updates - delays, cancellations, changed routes

Service alerts - stop moved, unforeseen events affecting a station, route or the entire network

Vehicle positions - information about the vehicles including location and congestion level

Supplying three examples of each one.

**field_analysis_api_BODS.py:**

For Vehicle Positions data accessed via the BODS GTFS API.

Listing the fields which are present across the positions supplied. Then analysing what types of values are present in the enumerated fields, and how many of the positions supply a value for each type of field.


**field_analysis_api_NSW.py:**

For Vehicle Positions data accessed via the NSW GTFS API.

Listing the fields which are present across the positions supplied. Then analysing what types of values are present in the enumerated fields, and how many of the positions supply a value for each type of field.

**field_analysis_bin.py:**

For Vehicle Positions data accessed via a supplied GTFS bin file.

Listing the fields which are present across the positions supplied. Then analysing what types of values are present in the enumerated fields, and how many of the positions supply a value for each type of field.

Generates a CSV and a pandas datarfame as a converted export of the bin file.

**GTFS_API_Request.py:**

For one off queries to the BODS GTFS API, storing the response in a readable .csv file and into a pandas dataframe.
You can select to have the script run with a query parameter of  week ago or 1 hour ago or 1 minute ago, just comment out the params you do not want:
    'startTimeAfter': get_unix_timestamp_one_hour_ago(),
    'startTimeAfter' = get_unix_timestamp_one_minute_ago()
    'startTimeAfter': get_unix_timestamp_one_week_ago(),
    'api_key': api_key



# How to Run the Files

This repository contains Python files that depend on Protocol Buffers. Follow these steps to set up and run the files:

# Prerequisites

- **Git**: Install Git to clone the repository. Download it from [git-scm.com](https://git-scm.com/).
- **Python**: Required to run the files. Download from [python.org](https://www.python.org/).
- **Protocol Buffers Compiler (protoc)**: Required to compile `.proto` files.

# Steps

1. **Clone the Repository**:
   ```
   git clone https://github.com/benjamesmurray/GTFS
   ```

2. **Navigate to the Repository Directory**:
   ```
   cd [Name of the repository]
   ```
   Replace `[Name of the repository]` with the directory name of the cloned repository.

3. **Install Required Python Packages** (if applicable):
   Install the required Python packages:
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


7. **Set up your API key**:
   - Set your API key in the terminal using:
     ```
     setx GTFS_API_KEY "Your-API-Key-Here"
     ```
   - Replace `Your-API-Key-Here` with your BODS API key.

8. **Run the Python Files**:
   - Execute the Python scripts using:
     ```
     python filename.py
     ```
   - Replace `filename.py` with the name of the Python file you want to run.

# Additional Notes

- Ensure you are in the correct directory when executing commands.
- For additional setup or running parts of a larger application, refer to specific instructions provided in the repository.

# Additional detail on Protocol Buffers Compiler (protoc) and .proto files

- What are Protocol Buffers? 

Protocol Buffers (Protobuf) are a language-neutral, platform-neutral, extensible mechanism for serializing structured data, similar to XML or JSON but more efficient and smaller. They are developed by Google and are used to define how data should be structured and then use this structure to serialize (convert data into a stream of bytes) and deserialize (convert bytes back into data) efficiently.

- What are .proto files?

 .proto files are where you define your data structure in a language-agnostic way. You specify the data types and structure you want, using a syntax that's reminiscent of C or Java but simpler. These files are plain text and include definitions for simple data types such as integers, booleans, and strings, as well as complex types, which are essentially custom structures you can define yourself.

- What is the Protocol Buffers Compiler (protoc)?

protoc is the tool that reads your .proto files and compiles them into code in your chosen programming language (like Python, Java, C++, etc.). This generated code includes methods for serializing your structured data to an efficient binary format and then deserializing it back. The process is as follows:

1. Define Data Structure: You start by defining the structure of your data in a .proto file. This includes specifying which fields are strings, numbers, booleans, or even other complex types you've defined.

2. Run protoc Compiler: Once your .proto file is ready, you use the protoc compiler on it. This process requires you to specify the target language you want the code to be generated in. protoc reads your .proto file and generates source code files in the language you've specified. This code includes all the necessary methods to serialize and deserialize the data structures you've defined.

3. Use in Your Application: With the generated code, you can now serialize your structured data to a compact binary format, which can be easily stored or sent over a network. You can also deserialize data received in this binary format back into usable structured data in your application.

- Analogy

Imagine you're sending a letter (your data) overseas (over a network). However, sending the whole letter (structured data) as is can be expensive and slow. So, you use a special method (Protocol Buffers) to encode this letter into a secret code (serialize it) that only you and the recipient know how to decode (deserialize). The .proto file is like the dictionary that defines this secret code, and protoc is the tool that translates your letter into and from this secret code according to the dictionary's rules.

By using Protocol Buffers, you ensure that your data is transmitted in a much more efficient and compact form than sending the whole letter, saving both time and resources in the process.

```
