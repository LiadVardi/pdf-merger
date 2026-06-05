import os
import subprocess
import sys

# Function to check and install a package
def install_package(package):
    print(f"Attempting to install {package}...")
    try:
        # Use pip to install the package within the current Python environment
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"Successfully installed {package}.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing {package}: {e}")
        sys.exit(1) # Exit if installation fails

# Check for pypdf and install if not found
try:
    from pypdf import PdfWriter
except ImportError:
    print("pypdf not found.")
    install_package("pypdf")
    from pypdf import PdfWriter # Try importing again after installation

# Define the file names
file1 = "first_file"
file2 = "second_file"
output_name = "Combined_file.pdf"

print(f"Starting PDF merge process for {file1} and {file2}...")

# Create a PdfWriter object (used now for merging)
merger = PdfWriter()

# Append the PDFs in the desired order
if os.path.exists(file1) and os.path.exists(file2):
    merger.append(file1)
    merger.append(file2)
    
    # Write the combined PDF to the output file
    with open(output_name, "wb") as output_file:
        merger.write(output_file)
    
    merger.close()
    print(f"\nSuccess: Successfully merged files into {output_name}")
else:
    print(f"Error: One or both input files were not found in the current directory: {file1}, {file2}")

