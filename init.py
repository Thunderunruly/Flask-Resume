import subprocess
import sys

def install_requirements(requirements_file):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "-r", requirements_file])
        print(f"Dependencies from '{requirements_file}' have been installed or upgraded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies. Error: {e}")

if __name__ == "__main__":
    requirements_file = "requirements.txt"
    install_requirements(requirements_file)
