# Comparing energy consumption between rendering modes in Blender

*Matthijs Vossen, Melle Koper, Roan Rosema, Scott Jochems*

*abstract hier*

## Introduction
In the world of digital content creation, rendering is a crucial process that transforms 3D models into high-quality images or animations. This process can be computationally intensive and often requires significant energy consumption.

Blender, a popular open-source 3D rendering tool, offers multiple rendering modes, mainly utilizing either the CPU or GPU. Each mode has its advantages: CPU rendering is often more accurate but can be slower, while GPU rendering is generally faster but may consume more power. Given the growing emphasis on energy-efficient computing, we want to investigate the differences in energy consumption between these two rendering approaches.

Our hypothesis is that GPU rendering, despite its efficiency in speed, may lead to higher energy consumption due to its increased computational power. To test this, we designed an experiment comparing the energy usage of CPU and GPU rendering in Blender. By automating the measurement process and ensuring a structured methodology, we aim to provide insights into the sustainability of rendering workflows.

In this blog, we will present our experimental setup, analyze our results and provide a discussion about our findings. Finally, we will provide recommendations for others to decrease their energy consumption.


## Background?


## Methodology

### Experimental Setup
To measure the energy consumption of different rendering modes in Blender, we designed an automated experiment that runs Blender rendering tasks using either the CPU or GPU while tracking power usage. The key components of our setup include:

- `Blender`: An open-source 3D graphics software.
- `energibridge`: A power measurement tool that monitors and logs energy consumption.
- `python` automation script: A custom script that manages the execution of experiments, collects data, and ensures reproducibility.

For our experiments, we used the following `Blender` scenes:
- donut.blend (include image)

### Experiment Design
We performed rendering tasks under two different conditions:
- CPU Rendering: Blender renders the scene using only the CPU, the CPU is limeted to 90% of its cores due to issues with energibridge.
- GPU Rendering: Blender renders the scene using the GPU when available.

Each experiment measured:
- Total energy consumption (Joules)
- Rendering duration (seconds)

To ensure reliable results, we ran 30 iterations per mode, alternating CPU and GPU runs randomly to avoid systematic biases due to system state changes.

### Automation Process
The experiment was fully automated using a Python script. The script follows these steps:

1. **Prepare the environment**:
   - Ensure that required directories exist.
   - Initialize a results file.

2. **Run an experiment**:
   - Construct and execute the `energibridge` command to measure energy consumption.
   - Launch Blender in background mode with the specified rendering configuration (CPU or GPU).
   - Capture `energibridge` output and extract energy and duration using regular expressions.
   - Log the results in a CSV file.

3. **Pause between runs**:
   - Introduce a short delay (one minute) between experiments to ensure proper measurement cleanup between runs.

4. **Repeat for all runs**:
   - Run 30 experiments per mode (CPU and GPU), randomly interleaved.

### Data Collection and Processing
The energy measurements and execution times are stored in a CSV file for stastical analysis.

### Hardware setup
All experiments were conducted on the same machine (hier specificeren hoe en wat).
|Operating System | CPU | GPU |
|Windows 10 | Intel Core I7-8750H | Nividia Quadro P1000|

### Reproducibility
To facilitate replication of our results, we provide:
- The Python script used for automation.
- Configuration details of the environment (Blender version, hardware specifications, etc.).

## Results

## Discussion
Add context for energy units (example household energy consumption).

## Limitations & Future Work
Issue with energibridge overflow when cpu usage goes to 100\%
