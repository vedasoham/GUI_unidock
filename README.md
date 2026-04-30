<div align="center">

# GUI-UniDock
### Graphical user interface for high-performance GPU-accelerated molecular docking interface.

<!-- CORE TECHNOLOGY STACK -->
<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/GPU_Acceleration-76B900?style=for-the-badge&logo=nvidia&logoColor=white" />
  <img src="https://img.shields.io/badge/Molecular Docking-14b8a6?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-GPL--3.0-blue?style=for-the-badge" />
</p>

---

### Overview
**GUI_UniDock** provides a user-friendly graphical interface for **Uni-Dock**, a cutting-edge docking engine that leverages GPU acceleration to achieve up to **10-fold speedup** over traditional CPU methods. This project simplifies high-throughput virtual screening, allowing researchers to manage complex docking simulations with a good precision.

---

### User Interface
<img src="https://github.com/vedasoham/GUI_unidock/blob/main/asset/1.png?raw=true" width="100%" alt="GUI Interface Preview" />

</div>

### Core Features & Performance
* **10-fold Acceleration**: Harnesses the full power of CUDA-enabled GPUs for massive-scale screening.
* **Multimodal Scoring**: Full support for `vina`, `vinardo`, and `ad4` scoring functions.
* **Interactive Grid Calibration**: Real-time 3D visualization and adjustment of the docking search space.
* **Job Telemetry**: Live monitoring of docking progress and computational resource utilization.

---

### Performance and specifications
*Benchmarks compared to traditional CPU-based Autodock Vina.*

| Metric | Uni-Dock (GPU) | Traditional Vina (CPU) |
| :--- | :--- | :--- |
| **Throughput** | High-Velocity Screening | Standard Throughput |
| **Acceleration** | **~10x** | 1x (Baseline) |
| **Efficiency** | Energy-Optimized | High CPU Overhead |

---

### Getting Started

#### Prerequisites
* **Python**: 3.10 or higher.
* **Uni-Dock Engine**: Must be installed as per the [official guide](https://github.com/dptech-corp/Uni-Dock).

#### Installation & Deployment
```bash
# Clone this repository
git clone [https://github.com/vedasoham/GUI_unidock.git](https://github.com/vedasoham/GUI_unidock.git)
cd GUI_unidock

# Initialize the environment
python setup.py

# Launch the interface
python app.py
```

---

### License
This project is licensed under the GPL-3.0 License - see the LICENSE file for details.

---

### Citation
If you utilize the GUI interface of the tool then please cite the original framework and our graphical implementation:

* **Original Framework**: [Yu, Yuejiang, et al. "Uni-dock: Gpu-accelerated docking enables ultralarge virtual screening." Journal of chemical theory and computation 19.11 (2023): 3336-3345](https://pubs.acs.org/doi/10.1021/acs.jctc.2c01145)
* **Source Implementation**: [Original Uni-Dock GitHub](https://github.com/dptech-corp/Uni-Dock).
* **Our Github Repository: [Uni-Dock GUI interface] (https://github.com/vedasoham/GUI_unidock.git)

---

**CONTACT for COLLABORATION**: `thedrsoham[at]gmail[dot]com` | `2401001030[at]gbu[dot]edu[dot]in`
[Computational and eXperimental Biomolecular Lab](https://github.com/cxbl-gbu)

<div align="center">
*"Not the end, but the beginning of a mission."*

</div>
