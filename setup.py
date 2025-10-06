import subprocess
import sys
import os
import threading
import re
import time


# Function to install Python packages using pip
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


# Function to install Python package requirements
def install_requirements():
    required_packages = [
        'numpy', 'pandas', 'py3Dmol', 
        'biopython', 'flask'
    ]
    print("Installing required Python packages...")
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing {package}...")
            install(package)


# Function to check CMake version
def is_cmake_version_supported(min_version="3.16.0"):
    try:
        output = subprocess.check_output(["cmake", "--version"], text=True)
        version_match = re.search(r"version (\d+\.\d+\.\d+)", output)
        if version_match:
            current_version = version_match.group(1)
            print(f"Found CMake version: {current_version}")
            return current_version >= min_version
        else:
            print("CMake version not detected.")
            return False
    except subprocess.CalledProcessError:
        print("CMake is not installed.")
        return False


# Function to remove old CMake installation and install a new version if necessary
def install_cmake():
    if is_cmake_version_supported():
        print("CMake is already installed with a supported version.")
        return

    # Remove existing CMake files
    print("Removing existing CMake installation...")
    try:
        # Locate the CMake installation path
        cmake_path = subprocess.check_output(["which", "cmake"], text=True).strip()
        cmake_dir = os.path.dirname(cmake_path)
        print(f"Removing CMake files from: {cmake_dir}")
        
        # Remove CMake-related binaries
        for cmake_binary in ["cmake", "ccmake", "cpack", "ctest"]:
            binary_path = os.path.join(cmake_dir, cmake_binary)
            if os.path.exists(binary_path):
                subprocess.run(["sudo", "rm", binary_path], check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error removing old CMake installation: {e}")
        sys.exit(1)

    # Download and install CMake 3.16.8
    print("Installing CMake 3.16.8...")
    cmake_url = "https://cmake.org/files/v3.16/cmake-3.16.8-Linux-x86_64.tar.gz"
    cmake_tar = "cmake-3.16.8-Linux-x86_64.tar.gz"
    try:
        # Download and extract CMake
        subprocess.run(["wget", cmake_url], check=True)
        subprocess.run(["tar", "-zxvf", cmake_tar], check=True)

        # Move CMake to /opt and create symlinks
        subprocess.run(["sudo", "mv", "cmake-3.16.8-Linux-x86_64", "/opt/cmake"], check=True)
        subprocess.run(["sudo", "ln", "-sf", "/opt/cmake/bin/cmake", "/usr/local/bin/cmake"], check=True)
        subprocess.run(["sudo", "ln", "-sf", "/opt/cmake/bin/cpack", "/usr/local/bin/cpack"], check=True)
        subprocess.run(["sudo", "ln", "-sf", "/opt/cmake/bin/ctest", "/usr/local/bin/ctest"], check=True)

        # Verify the new CMake version
        subprocess.run(["cmake", "--version"], check=True)
        print("CMake 3.16.8 installed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error during CMake installation: {e}")
        sys.exit(1)


# Function to install system dependencies like git
def install_system_dependencies():
    print("Installing git...")
    try:
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "git"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error installing git: {e}")
        sys.exit(1)


# Function to check if Boost is installed
def is_boost_installed():
    boost_include_dir = os.path.expanduser("~/local/boost/include")
    if os.path.exists(boost_include_dir):
        print(f"Boost is already installed in {boost_include_dir}.")
        return True
    return False


# Function to manually install Boost
def install_boost():
    if is_boost_installed():
        return os.path.expanduser("~/local/boost")

    print("Installing Boost manually...")
    boost_url = "https://archives.boost.io/release/1.82.0/source/boost_1_82_0.tar.gz"
    boost_tar = "boost_1_82_0.tar.gz"
    boost_dir = "boost_1_82_0"
    boost_install_dir = os.path.expanduser("/usr/local/")

    if not os.path.exists(boost_install_dir):
        try:
            subprocess.run(["wget", boost_url], check=True)
            subprocess.run(["tar", "-xvzf", boost_tar], check=True)

            # Build and install Boost
            os.chdir(boost_dir)
            print("Building and installing Boost...")
            subprocess.run(["./bootstrap.sh", f"--prefix={boost_install_dir}"], check=True)
            subprocess.run(["./b2", "install", f"--prefix={boost_install_dir}"], check=True)

            print(f"Boost installed to {boost_install_dir}")
            os.chdir("..")
        except subprocess.CalledProcessError as e:
            print(f"Error during Boost installation: {e}")
            sys.exit(1)
    else:
        print(f"Boost is already installed in {boost_install_dir}")

    return boost_install_dir


# Function to build UniDock with password
def build_unidock_with_password(update_callback, password, stop_flag, boost_install_dir):
    """
    Clones and builds UniDock using CMake, with manual Boost setup.
    Requires sudo for installation, and the password is provided by the user.
    Uses update_callback to send updates to the console.
    """
    try:
        # Repository details
        repo_url = "https://github.com/dptech-corp/Uni-Dock.git"
        build_dir = os.path.join(os.getcwd(), "Uni-Dock/unidock")
        
        # Check if UniDock repository exists
        if not os.path.exists("Uni-Dock"):
            update_callback("Cloning UniDock repository...")
            subprocess.run(["git", "clone", repo_url], check=True)
            time.sleep(2)
            update_callback("Repository cloned successfully.")
        else:
            update_callback("Repository already exists. Skipping cloning.")
        
        if not os.path.exists(build_dir):
            raise Exception("Failed to find UniDock directory.")
        
        # Check if the stop flag is set
        if stop_flag.is_set():
            update_callback("Build process stopped.")
            return False
        
        update_callback(f"Navigating to the UniDock directory: {build_dir}")
        
        # Configure CMake with manual Boost setup
        update_callback("Configuring build with CMake...")
        try:
            cmake_command = [
                "cmake", "-B", "build",
                f"-DBOOST_ROOT={boost_install_dir}",  # Use the custom Boost installation
                "-DFETCH_BOOST=OFF"  # Prevent CMake from fetching Boost
            ]
            subprocess.run(cmake_command, cwd=build_dir, check=True)
            time.sleep(2)
            update_callback("Configuration successful.")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error during CMake configuration: {str(e)}")
        
        # Check if the stop flag is set
        if stop_flag.is_set():
            update_callback("Build process stopped.")
            return False
        
        # Build UniDock
        update_callback("Building UniDock...")
        try:
            subprocess.run(["cmake", "--build", "build", "-j8"], cwd=build_dir, check=True)
            time.sleep(2)
            update_callback("Build completed successfully.")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error during build process: {str(e)}")
        
        # Check if the stop flag is set
        if stop_flag.is_set():
            update_callback("Build process stopped.")
            return False
        
        # Install UniDock using sudo
        update_callback("Installing UniDock...")
        try:
            # Run the install command with sudo, passing the password through a pipe
            install_command = f"echo {password} | sudo -S cmake --install build"
            result = subprocess.run(install_command, shell=True, cwd=build_dir, text=True, capture_output=True)
            
            if result.returncode == 0:
                update_callback("UniDock installed successfully.")
                return True
            else:
                update_callback(f"Build error: {result.stderr.strip()}")
                return False
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error during installation process: {str(e)}")
    
    except Exception as e:
        update_callback(f"An unexpected error occurred: {str(e)}")
        return False


# Function to get password input from the user
def get_password():
    return input("Enter your sudo password: ")


# Main function for the setup process
def main():
    print("=" * 60)
    print("UniDock GUI Installation Script")
    print("=" * 60)
    
    # Step 1: Install Python packages
    print("\n[Step 1/6] Installing Python packages...")
    install_requirements()
    
    # Step 2: Install CMake (with version check)
    print("\n[Step 2/6] Checking and installing CMake...")
    install_cmake()
    
    # Step 3: Install git
    print("\n[Step 3/6] Installing system dependencies...")
    install_system_dependencies()
    
    # Step 4: Install Boost manually (only if not already installed)
    print("\n[Step 4/6] Installing Boost library...")
    boost_install_dir = install_boost()
    
    # Step 5: Prompt user for password
    print("\n[Step 5/6] Preparing to build UniDock...")
    password = get_password()
    
    # Step 6: Build UniDock with manual Boost path
    print("\n[Step 6/6] Building and installing UniDock...")
    stop_flag = threading.Event()
    
    def update_callback(message):
        print(f"    {message}")
    
    success = build_unidock_with_password(update_callback, password, stop_flag, boost_install_dir)
    
    print("\n" + "=" * 60)
    if success:
        print("Setup complete! UniDock has been built successfully.")
    else:
        print("Setup encountered errors. Please check the output above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
