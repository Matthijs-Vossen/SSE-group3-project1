import subprocess
import time
import random
import csv
import re
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

# Constants and Configuration
BLENDER_EXECUTABLE = r"FILE PATH TO BLENDER EXECUTABLE"  # Use raw string
BLEND_FILE = r"FILE PATH TO .blend FILE"  # Adjusted for Windows path format
RENDER_SCRIPT = r"render_script.py"  # Custom Blender Python script
ENERGIBRIDGE_PATH = r"FILE PATH TO ENERGIBRIDGE.exe"  # Ensure .exe for windows
CSV_FILE_LOCATION = r"../results/experiment_results_1.csv"
OUTPUT_DIR = r"../results/energibridge-outputs"
PAUSE_BETWEEN_RUNS = 60  # seconds
MEASUREMENT_INTERVAL = "500"  # in milliseconds

# Precompiled regex to parse energy and duration from the tool output.
ENERGY_REGEX = re.compile(
    r"Energy consumption in joules:\s*([\d\.]+).*?([\d\.]+)\s*sec",
    re.DOTALL
)

def ensure_directories():
    """Ensure necessary directories exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def log_experiment_result(run_type: str, run_number: int, energy: float, duration: float):
    """Append a single experiment result to the CSV file."""
    with open(CSV_FILE_LOCATION, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([run_type, run_number, energy, duration])

def run_experiment(run_type: str, run_number: int):
    measurement_output = os.path.join(OUTPUT_DIR, f"power_measure_{run_type}_run{run_number}.csv").replace("\\", "/")

    measurement_cmd = [
        ENERGIBRIDGE_PATH,
        "--output", measurement_output,
        "--interval", MEASUREMENT_INTERVAL,
        "--summary"
    ]

    # if run_type == "gpu":
    #     measurement_cmd.append("-g")

    blender_cmd = [
        BLENDER_EXECUTABLE,
        "--background",
        BLEND_FILE,
        "--python", RENDER_SCRIPT,
        "--",
        f"--render_mode={run_type}"
    ]

    measurement_cmd += blender_cmd

    logging.info(f"Starting run {run_number} ({run_type})")

    try:
        result = subprocess.run(
            measurement_cmd,
            capture_output=True,
            text=True,
            check=True
        )

        output_str = result.stdout
        # error_str = result.stderr
        logging.info("Energibridge output:\n%s", output_str)
        # logging.error("Energibridge error output:\n%s", error_str)

        match = ENERGY_REGEX.search(output_str)
        if match:
            energy = float(match.group(1))
            duration = float(match.group(2))
            log_experiment_result(run_type, run_number, energy, duration)
            logging.info(
                f"Run {run_number} ({run_type}): Energy={energy} joules, Duration={duration} sec"
            )

        else:
            logging.warning(f"Could not parse energy data from run {run_number} ({run_type}).")

        time.sleep(PAUSE_BETWEEN_RUNS)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during run {run_number} ({run_type}): {e}")
        logging.error(f"Command output: {e.output}")
        logging.error(f"Command stderr: {e.stderr}")
    logging.info(f"Completed run {run_number} ({run_type})\n{'-'*40}")

def main():
    total_runs_per_mode = 30  # Total runs for each mode.
    
    # Build a shuffled list of experiments to interleave CPU and GPU runs.
    experiments = (
        [("cpu", i) for i in range(1, total_runs_per_mode + 1)] +
        [("gpu", i) for i in range(1, total_runs_per_mode + 1)]
    )
    random.shuffle(experiments)
    
    ensure_directories()
    
    # Write the header to the CSV file.
    with open(CSV_FILE_LOCATION, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["run_type", "run_number", "energy_joules", "execution_time_sec"])
    
    # Execute each experiment.
    for run_type, run_number in experiments:
        run_experiment(run_type, run_number)

if __name__ == "__main__":
    assert os.path.isfile(BLENDER_EXECUTABLE), f"Blender executable not found: {BLENDER_EXECUTABLE}"
    assert os.path.isfile(BLEND_FILE), f"Blend file not found: {BLEND_FILE}"
    assert os.path.isfile(ENERGIBRIDGE_PATH), f"Energibridge executable not found: {ENERGIBRIDGE_PATH}"
    assert os.path.isdir(os.path.dirname(CSV_FILE_LOCATION)), f"CSV file directory not found: {os.path.dirname(CSV_FILE_LOCATION)}"
    assert os.path.isdir(OUTPUT_DIR), f"Output directory not found: {OUTPUT_DIR}"
    assert os.path.isfile(RENDER_SCRIPT), f"Render script not found: {RENDER_SCRIPT}"
    main()
