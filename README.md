# SSE-group3-project1

## Overview

This repository contains two Python scripts that automate running Blender renders on both CPU and GPU, measuring energy consumption with [Energibridge](https://github.com/YourOrg/Energibridge) (or a similar tool), and logging the results to a CSV file. Specifically:

1. **`render_script.py`** (Blender Python Script)  
   - Invoked by Blender in headless (`--background`) mode.
   - Configures the Blender Cycles render engine to use either CPU or GPU devices based on command-line arguments.
   - Starts a render and then gracefully exits Blender.

2. **`experiments.py`** (Main Orchestration Script)  
   - Called from your system Python environment (not Blender’s internal Python).
   - Automatically runs a set of CPU and GPU render tests using Blender in the background.
   - Uses `Energibridge.exe` (or your measurement tool) to measure energy consumption and execution time.
   - Logs the results to a CSV file.

## How It Works

1. **`experiments.py`**:
   - Defines file paths for:
     - **Blender executable** (e.g., `C:/Program Files/Blender Foundation/Blender 3.0/blender.exe`)
     - **Blend file** (e.g., `data/Donut.blend`)
     - **Energibridge.exe** (a power measurement tool)
   - Interleaves a set of CPU and GPU tests, so that a GPU test follows a CPU test randomly (to avoid systematic bias).
   - For each test run:
     1. Invokes `Energibridge.exe` with the measurement interval and output file path.
     2. Executes Blender in headless mode (`--background`) passing in the `render_script.py` via `--python`.
     3. Tells `render_script.py` whether to use CPU or GPU rendering via `-- --render_mode=cpu` or `-- --render_mode=gpu`.
     4. Collects and parses the total energy consumption (in joules) and execution time (in seconds) reported by Energibridge.
     5. Logs these metrics to a CSV file (configured in `CSV_FILE_LOCATION`).

2. **`render_script.py`**:
   - Runs inside Blender (in headless mode).
   - Reads custom command-line arguments (after the `--` separator).
   - Configures the Cycles engine to use CPU or GPU.
   - Renders a frame (without writing to a file by default).
   - Quits Blender after a brief pause.

## Requirements

- **Blender** (tested with Blender 4.1).
- **Energibridge** (or a similar power-measurement CLI tool that logs energy usage).
- A **.blend file** containing the scene you want to render.
- **Python 3.x** installed (for running `experiments.py`).

## Setup Instructions

1. **Clone or download** this repository.
2. **Update paths in `experiments.py`:**
   - `BLENDER_EXECUTABLE`: Full path to your Blender `blender.exe`.
   - `BLEND_FILE`: Full path to your .blend file.
   - `ENERGIBRIDGE_PATH`: Full path to your `Energibridge.exe`.
   - `CSV_FILE_LOCATION`: Where you want the CSV logs to be saved (e.g., `../results/experiment_results_1.csv`).
   - `OUTPUT_DIR`: Where Energibridge’s detailed output should be stored.
3. **(Optional) Adjust other parameters**:
   - `PAUSE_BETWEEN_RUNS`: Number of seconds to wait between runs.
   - `MEASUREMENT_INTERVAL`: Measurement interval used by Energibridge, in milliseconds.
   - `total_runs_per_mode` inside `main()`: Number of CPU and GPU runs.
4. **Ensure directories exist** (or let the script create them if configured properly).
5. **Run the experiment**:
   - Open a command prompt or terminal and navigate to the folder containing `experiments.py`.
   - Execute: `python experiments.py`
   - The script will:
     - Verify required files and directories.
     - Generate a CSV with a header row.
     - Randomize the experiment order for CPU/GPU runs.
     - For each run:
       - Launch Energibridge and Blender in headless mode.
       - Capture results.
       - Append them to the CSV file.
       - Wait `PAUSE_BETWEEN_RUNS` seconds before the next run.

**Note**: The entire sequence can take a while depending on your scenes, number of runs, and hardware.

## Example CSV Output

| run_type | run_number | energy_joules | execution_time_sec |
|----------|-----------:|--------------:|-------------------:|
| cpu      | 1         | 123.45        | 20.5               |
| gpu      | 1         | 98.76         | 18.2               |
| ...      | ...       | ...           | ...                |