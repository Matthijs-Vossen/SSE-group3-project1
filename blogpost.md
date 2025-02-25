# Comparing energy consumption between rendering modes in Blender

*Matthijs Vossen, Melle Koper, Roan Rosema, Scott Jochems*

In modern digital content creation pipelines, rendering can be a major bottleneck—not only in terms of time but also energy consumption. As sustainability becomes a priority, understanding the energy footprint of different rendering modes in Blender is essential for individuals, studios, and the broader 3D community. In this study, we compare the energy usage of CPU versus GPU rendering on multiple machines using an automated pipeline. We present our experimental setup, discuss our findings, and propose recommendations for more sustainable rendering practices.

## Introduction
In the world of digital content creation, rendering is a crucial process that transforms 3D models into high-quality images or animations. This process can be computationally intensive and often requires significant energy consumption.

Blender, a popular open-source 3D rendering tool, offers multiple rendering modes, mainly utilizing either the CPU or GPU. Each mode has its advantages: CPU rendering is often more accurate but can be slower, while GPU rendering is generally faster but may consume more power. Given the growing emphasis on energy-efficient computing, we want to investigate the differences in energy consumption between these two rendering approaches.

Our hypothesis is that GPU rendering, despite its efficiency in speed, may lead to higher energy consumption due to its increased computational power. To test this, we designed an experiment comparing the energy usage of CPU and GPU rendering in Blender. By automating the measurement process and ensuring a structured methodology, we aim to provide insights into the sustainability of rendering workflows.

In this blog, we will present our experimental setup, analyze our results, and provide a discussion about our findings. Beyond raw numbers, we’ll also explore why these results matter—shedding light on who is most affected and how small differences in energy consumption can translate into large impacts at scale. Finally, we will give recommendations for those looking to optimize their rendering pipeline for energy efficiency.


## Background?

Energy consumption in software systems has become a critical topic as organizations and individuals become more environmentally conscious. Large production studios, for instance, often maintain render farms running 24/7 to meet project deadlines[^1]. Even a slight improvement in energy efficiency can translate into substantial cost savings and a reduced carbon footprint over thousands of render jobs.

[^1]: Patoli, Muhammad Zeeshan, et al. "An open source grid based render farm for blender 3d." 2009 IEEE/PES Power Systems Conference and Exposition. IEEE, 2009.

For freelancers and hobbyists, rendering might happen on a single workstation or laptop. While the scale is smaller, energy usage still directly impacts electricity bills, thermal management, and hardware longevity. In addition, many cloud providers now offer GPU-based rendering services (e.g., AWS Deadline Cloud) [^2]; understanding the comparative energy draw of CPU vs. GPU modes can inform both pricing models and user choices.

[^2]: [AWS Deadline Cloud](https://aws.amazon.com/deadline-cloud/)

Why Blender?
- Popularity and Accessibility: As an open-source tool with a massive community, Blender is often a go-to for 3D enthusiasts and professionals.
- Flexibility: Blender’s support for both CPU and GPU rendering (not to mention various third-party render engines) provides a solid testing ground.
- Industry Adoption: From indie projects to big-budget movies, Blender is increasingly used across different production scales.

By focusing on Blender, this study’s findings have relevance for a broad audience—including individual artists, small studios, large production houses, and cloud service providers aiming to optimize sustainability in their pipelines.

## Methodology

### Experimental Setup
To measure the energy consumption of different rendering modes in Blender, we designed an automated experiment that runs Blender rendering tasks using either the CPU or GPU while tracking power usage. The key components of our setup include:

- `Blender`: An open-source 3D graphics software.
- `energibridge`: A power measurement tool that monitors and logs energy consumption.
- `python` automation script: A custom script that manages the execution of experiments, collects data, and ensures reproducibility.

For our experiments, we used the Donut.blend scene [^3].
![An image of what the Donut.blend scene looks like](./data/donut.png)

[^3]: [Link](https://free3d.com/3d-model/donut-716088.html) to Donut.blend file

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
To understand the difference between CPU and GPU processing we ran the experiments on 3 different machines. Each machine ran 30 experiments per mode, randomly interleaved. 
|Operating System | OS Build | CPU | GPU | RAM |
| ---- | ----- | ----- | ---- | ---- |
| Windows 10 | `vul build in` | Intel Core I7-8750H | Nividia Quadro P1000 | `vul ram in` |
| Windows 10 22H2 | 19045.5487 | AMD Ryzen 5 5600X | Nvidia GeForce RTX 3060 | 16 GB |
| Mac OS | 15.3.1 | M1 chip | M1 chip | 8 GB |

### Reproducibility
To facilitate replication of our results, we provide:
- The Python script used for automation which can be found [here](https://github.com/Matthijs-Vossen/SSE-group3-project1).
- Python version: 3.9
- Blender version: 4.3
- Configuration details of the environment (Blender version, hardware specifications, etc.).

## Results

## Discussion
Add context for energy units (example household energy consumption).

## Limitations & Future Work
Issue with energibridge overflow when cpu usage goes to 100\%
1. Measurement Constraints:
	- We encountered issues with energibridge overflow when CPU usage goes to 100%. This required limiting CPU usage to 90%, potentially impacting the full “real-world” scenario of 100% CPU load.
	- Background processes and thermal throttling could skew results slightly, even though we attempted to control these factors by alternating runs and introducing cooldown periods.
2. Scene Complexity & Variety:
	- We tested a single donut scene. Results may differ for more complex scenes with advanced features (e.g., volumetrics, hair particles) or simpler scenes with fewer geometry/texture requirements.
3. Hardware Specifics:
	- Our tests covered a limited range of CPUs and GPUs. Different architectures (AMD GPUs, Intel Arc, etc.) or multi-GPU setups could yield different energy profiles.
	- Apple Silicon (M1) is unique in its integrated CPU-GPU design, which may not generalize to discrete GPUs.
4. Future Directions:
	- Multi-GPU Tests: Assess whether multiple GPUs in parallel save more energy per render compared to single GPUs.
	- Different Render Engines: Compare energy consumption across Blender’s Cycles, Eevee, or other engines like LuxCore or Octane.
	- Further Automation: Integrate real-time monitoring for thermals, fan speeds, or driver-level power states to provide a more holistic view of performance and efficiency.
