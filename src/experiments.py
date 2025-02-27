import subprocess
import time
import random
import csv
import re
import os
import logging

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

# ---------------------------------------------------------------------------
# Constants / Configuration
# ---------------------------------------------------------------------------

# Path to the Blender executable
BLENDER_EXECUTABLE = r"PATH\TO\BLENDER\blender.exe"

# Path to the .blend file you want to render
BLEND_FILE = r"data/Donut.blend"

# Path to the Python script that will run inside Blender
RENDER_SCRIPT = r"render_script.py"

# Path to the Energibridge executable (or another power measurement tool)
ENERGIBRIDGE_PATH = r"PATH\TO\energibridge.exe"

# Output CSV file (will be created or appended to)
CSV_FILE_LOCATION = r"../results/experiment_results_1.csv"

# Directory where the measurement results (raw CSV logs) will be stored
OUTPUT_DIR = r"../results/energibridge-outputs"

# Time to wait between runs (in seconds)
PAUSE_BETWEEN_RUNS = 60

# Measurement interval for Energibridge (in milliseconds)
MEASUREMENT_INTERVAL = "500"

# Regex pattern to parse energy and duration from Energibridge output
ENERGY_REGEX = re.compile(
    r"Energy consumption in joules:\s*([\d\.]+).*?([\d\.]+)\s*sec",
    re.DOTALL
)

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def ensure_directories():
    """
    Ensure all necessary output directories exist. 
    Creates them if they do not exist.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(CSV_FILE_LOCATION), exist_ok=True)

def log_experiment_result(run_type: str, run_number: int, energy: float, duration: float):
    """
    Appends a single experiment result to the CSV file.

    Args:
        run_type (str): "cpu" or "gpu"
        run_number (int): The trial number
        energy (float): The measured energy consumption (in joules)
        duration (float): The measured execution time (in seconds)
    """
    with open(CSV_FILE_LOCATION, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([run_type, run_number, energy, duration])

def run_experiment(run_type: str, run_number: int):
    """
    Runs a single experiment for either CPU or GPU.

    Steps:
      1. Build Energibridge command to measure power.
      2. Append Blender command in headless mode with appropriate arguments.
      3. Execute the combined command.
      4. Parse energy/duration from Energibridge's output.
      5. Log the results.
      6. Wait before next run.

    Args:
        run_type (str): "cpu" or "gpu"
        run_number (int): experiment iteration
    """
    # Output file for this measurement
    measurement_output = os.path.join(
        OUTPUT_DIR, f"power_measure_{run_type}_run{run_number}.csv"
    ).replace("\\", "/")

    # Build the power measurement command
    measurement_cmd = [
        ENERGIBRIDGE_PATH,
        "--output", measurement_output,
        "--interval", MEASUREMENT_INTERVAL,
        "--summary"
    ]

    # Build the Blender command
    blender_cmd = [
        BLENDER_EXECUTABLE,
        "--background",
        BLEND_FILE,
        "--python", RENDER_SCRIPT,
        "--",
        f"--render_mode={run_type}"
    ]

    # Combine them so Energibridge calls Blender
    measurement_cmd += blender_cmd

    logging.info(f"Starting run {run_number} ({run_type})")
    try:
        # Execute command and capture output
        result = subprocess.run(
            measurement_cmd,
            capture_output=True,
            text=True,
            check=True
        )

        output_str = result.stdout
        logging.info("Energibridge output:\n%s", output_str)

        # Parse energy and duration from the tool's summary output
        match = ENERGY_REGEX.search(output_str)
        if match:
            energy = float(match.group(1))
            duration = float(match.group(2))
            log_experiment_result(run_type, run_number, energy, duration)
            logging.info(
                f"Run {run_number} ({run_type}): "
                f"Energy={energy} joules, Duration={duration} sec"
            )
        else:
            logging.warning(
                f"Could not parse energy data from run {run_number} ({run_type})."
            )

    except subprocess.CalledProcessError as e:
        logging.error(f"Error during run {run_number} ({run_type}): {e}")
        logging.error(f"Command output: {e.output}")
        logging.error(f"Command stderr: {e.stderr}")

    # Wait a bit before the next run
    time.sleep(PAUSE_BETWEEN_RUNS)
    logging.info(f"Completed run {run_number} ({run_type})\n{'-'*40}")

# ---------------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------------

def main():
    """
    Main function to orchestrate CPU/GPU experiments.
    
    1. Set the number of runs per mode (CPU vs GPU).
    2. Shuffle them to avoid systematic bias.
    3. For each run:
       - Measure energy consumption and time.
       - Write results to a CSV.
    """
    total_runs_per_mode = 30  # Adjust as needed

    # Create a list of (run_type, run_number) pairs, then shuffle.
    experiments_list = (
        [("cpu", i) for i in range(1, total_runs_per_mode + 1)] +
        [("gpu", i) for i in range(1, total_runs_per_mode + 1)]
    )
    random.shuffle(experiments_list)

    # Ensure directories exist
    ensure_directories()

    # Write CSV header
    with open(CSV_FILE_LOCATION, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["run_type", "run_number", "energy_joules", "execution_time_sec"])

    # Execute each experiment in random order
    for run_type, run_number in experiments_list:
        run_experiment(run_type, run_number)

# Safety checks before launching the main experiment
if __name__ == "__main__":
    # Simple sanity checks
    assert os.path.isfile(BLENDER_EXECUTABLE), \
        f"Blender executable not found: {BLENDER_EXECUTABLE}"
    assert os.path.isfile(BLEND_FILE), \
        f"Blend file not found: {BLEND_FILE}"
    assert os.path.isfile(ENERGIBRIDGE_PATH), \
        f"Energibridge executable not found: {ENERGIBRIDGE_PATH}"
    assert os.path.isfile(RENDER_SCRIPT), \
        f"Render script not found: {RENDER_SCRIPT}"

    main()