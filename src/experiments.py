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
BLENDER_EXECUTABLE = "/Applications/Blender.app/Contents/MacOS/Blender"  # Adjust as needed.
BLEND_FILE = "../data/temple.blend"  # Replace with your actual .blend file.
RENDER_SCRIPT = "render_script.py"  # Replace with your custom Blender Python script.
ENERGIBRIDGE_PATH = "/Users/matthijsvossen/Documents/University/Delft/Year 2/Q3/Sustainable Software Engineering/Project 1/src/energibridge"  # Adjust as needed.
CSV_FILE_LOCATION = "../results/experiment_results.csv"
OUTPUT_DIR = "../results/energibridge-outputs"
PAUSE_BETWEEN_RUNS = 20  # seconds
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
    """
    Runs a single experiment by launching the energy measurement tool,
    which in turn launches Blender.

    Parameters:
        run_type (str): Either 'cpu' or 'gpu'.
        run_number (int): The current run number.
    """
    # Build the output path for the measurement log.
    measurement_output = os.path.join(OUTPUT_DIR, f"power_measure_{run_type}_run{run_number}.csv")
    
    # Construct the Blender command.
    blender_cmd = [
        BLENDER_EXECUTABLE,
        "--background",  # Run Blender in background mode.
        BLEND_FILE,
        "--python", RENDER_SCRIPT,
        "--",  # Subsequent args are for the Blender Python script.
        f"--render_mode={run_type}"
    ]
    
    # Build the energibridge command.
    measurement_cmd = [
        ENERGIBRIDGE_PATH,
        "--output", measurement_output,
        "--interval", MEASUREMENT_INTERVAL,
        "--summary"
    ]
    if run_type == "gpu":
        measurement_cmd.append("--gpu")
    
    # Append the Blender command to the measurement command.
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
        logging.info("Energibridge output:\n%s", output_str)
        
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
        
        # Pause to ensure proper measurement cleanup between runs.
        time.sleep(PAUSE_BETWEEN_RUNS)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during run {run_number} ({run_type}): {e}")

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
    main()