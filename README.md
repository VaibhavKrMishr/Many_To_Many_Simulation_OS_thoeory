# 🧵 Many-to-Many (M:N) Thread Model Simulator

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![UI](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Package Manager](https://img.shields.io/badge/Manager-uv-blue?logo=astral)](https://github.com/astral-sh/uv)

A high-fidelity, web-based simulation environment designed for educational exploration of **Thread Mapping Models** in Operating Systems. This project specifically focuses on the **Many-to-Many (M:N)** architecture, demonstrating its superiority in handling synchronous I/O and multi-core resource distribution.

---

## 🎯 Project Motivation
Thread management is a critical aspect of modern kernel design. While **Many-to-One** is efficient but lacks parallelism, and **One-to-One** provides parallelism but at a high kernel overhead, the **Many-to-Many** model offers a balanced approach. This simulator was built to visualize the complex interplay between User-Level Threads (ULTs) and Kernel-Level Threads (KLTs/LWPs), making abstract OS concepts tangible.

## ✨ Key Features
- **Deterministic Simulation Engine**: A tick-based logic core that accurately models context switching penalties, I/O blocking probabilities, and thread aging.
- **Dynamic LWP Scaling**: Real-time adjustment of $M$ (User) and $N$ (Kernel) parameters to observe performance bottlenecks.
- **Interactive Dashboard**:
    - **Live Thread Grid**: View the lifecycle of every thread (Ready, Running, Blocked, Finished).
    - **Resource Utilization**: Real-time tracking of LWP occupancy and system throughput.
    - **Completion Analytics**: Plotly-powered charts showing execution finality across time-steps.
- **Hybrid Task Modeling**: Supports both CPU-intensive computations and I/O-bound operations with distinct blocking behaviors.

## 🛠️ Technology Stack
- **Engine**: Python 3.x (Concurrency Simulation)
- **Frontend**: Streamlit (Premium Dark Aesthetic)
- **Visualization**: Plotly Graph Objects & Custom CSS Animations
- **Depedencies**: Managed via `uv` for lightning-fast environment resolution

---

## 🚀 Getting Started

### Prerequisites
Ensure you have [uv](https://github.com/astral-sh/uv) installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation & Execution
1. **Initialize & Run**:
   ```bash
   cd /path/to/OS_Theory
   uv run streamlit run app.py
   ```
2. **Access the Web UI**: Open your browser at `http://localhost:8501`.

---

## 📖 Core Concepts Modeled

### Thread Lifecycle
| State | Color | Description |
| :--- | :--- | :--- |
| **Ready** | 🟦 Blue | Thread is in the user-space queue, waiting for an LWP. |
| **Running** | 🟩 Green | Thread is actively mapped to a Kernel Thread and executing work. |
| **Blocked** | 🟥 Red | Thread is waiting for an I/O event. The LWP is free to pick another ULT. |
| **Finished** | ⬜ Grey | All work units completed; thread resources released. |

### The M:N Advantage
Unlike the Many-to-One model, when a thread in this simulator enters the **Blocked** state, the simulator demonstrates how the **Lightweight Process (LWP)** becomes available to execute other ready threads, maximizing CPU utilization.

---

## 📂 Project Structure
```text
OS_Theory/
├── app.py           # Streamlit application & Visualization logic
├── simulator.py     # Core logical engine (Thread & Scheduler classes)
├── THEORY.md        # Academic deep-dive into threading architectures
├── README.md        # Technical project overview (this file)
└── pyproject.toml   # Dependency specifications for uv
```

## 📊 Evaluation Metrics
- **Avg Wait Time**: The latency experienced by ULTs in the Ready Queue.
- **Context Switch Count**: Number of times an LWP switched its mapped ULT.
- **CPU Utilization**: Percentage of time Kernel Threads spent doing productive work.
- **Throughput**: Rate of task completion per simulation tick.

---
**Developed for OS Theory & Design Course Project**
