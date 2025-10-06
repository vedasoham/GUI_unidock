# GUI_UniDock

A user-friendly graphical user interface for Uni-Dock, a GPU-accelerated molecular docking program. This project is a collaboration between [Your Name/GitHub Username] and Atharva.

![image](https://github.com/dptech-corp/Uni-Dock/blob/main/unidock.png)
*Image from the official Uni-Dock repository.*

## About Uni-Dock

Uni-Dock is a high-performance molecular docking program that leverages the power of GPUs to accelerate the docking process by up to 2000 times compared to traditional CPU-based methods. It supports popular scoring functions like `vina`, `vinardo`, and `ad4`. Uni-Dock is part of the DeepModeling community and is designed for high-throughput virtual screening and molecular docking simulations.

## Features of the GUI

* **Easy-to-use Interface:** Simplifies the process of setting up and running docking simulations with Uni-Dock.
* **Input File Management:** Easily load and manage receptor and ligand files.
* **Configuration:** Interactively set up the docking parameters, including the search space, scoring function, and other advanced options.
* **Job Monitoring:** Monitor the progress of your docking jobs in real-time.
* **Results Visualization:** (Optional - if you have this feature) Visualize the docking results and analyze the binding poses.

## Getting Started

### Prerequisites

* Python 3.x
* Uni-Dock: Follow the official [Uni-Dock installation guide](https://github.com/dptech-corp/Uni-Dock) to install it on your system.
* (List any other dependencies your GUI has, for example, PyQt, Tkinter, etc.)

### Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/](https://github.com/)[Your-GitHub-Username]/[Your-Repository-Name].git
    ```
2.  Navigate to the project directory:
    ```bash
    cd [Your-Repository-Name]
    ```
3.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Launch the application by running the main Python script:
    ```bash
    python main.py
    ```
2.  (Add more specific instructions on how to use your GUI. You can include screenshots to make it clearer.)

    *Example:*
    * **Step 1:** Click on "Load Receptor" to select your protein PDB file.
    * **Step 2:** Click on "Load Ligand" to select your ligand MOL2/SDF file.
    * **Step 3:** Adjust the search space coordinates in the "Docking Configuration" panel.
    * **Step 4:** Click "Run Docking" to start the simulation.

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Acknowledgements

* The **Uni-Dock team** for developing the core docking program.
* **Atharva** for their collaboration on this GUI.
* (Any other acknowledgements you want to add)
