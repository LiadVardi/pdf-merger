import subprocess
import sys
from tkinter import messagebox


def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Install Error", f"Failed to install {package}:\n{e}")
        sys.exit(1)


try:
    import pypdf
except ImportError:
    install_package("pypdf")
    import pypdf

try:
    import customtkinter
except ImportError:
    install_package("customtkinter")
    import customtkinter
