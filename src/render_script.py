import bpy
import sys
import time
import multiprocessing

def parse_args():
    """
    Parse command-line arguments passed after the '--' separator.
    
    Expected argument:
      --render_mode=cpu   (or gpu)
    
    Returns:
        dict: A dictionary containing the parsed arguments.
    """
    argv = sys.argv
    if "--" not in argv:
        return {}

    # Extract all custom arguments after the '--' separator.
    custom_args = argv[argv.index("--") + 1:]
    args = {}
    for arg in custom_args:
        if arg.startswith("--render_mode="):
            # Remove any whitespace and convert the mode to lowercase.
            args["render_mode"] = arg.split("=", 1)[1].strip().lower()
    return args

def configure_render_device(render_mode: str) -> None:
    """
    Configure the Cycles render device based on the specified render mode.

    Args:
        render_mode (str): Either 'cpu' or 'gpu'.
    """
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    print("scene.render.engine", scene.render.engine)

    if render_mode == "gpu":
        print("Configuring render settings for GPU...")

        scene.cycles.device = 'GPU'

        try:
            prefs = bpy.context.preferences
            cprefs = prefs.addons["cycles"].preferences

            print(cprefs.compute_device_type)
            # Set the device type to GPU if available (CUDA/Optix for NVIDIA, OpenCL for AMD)
            if cprefs.compute_device_type == 'CUDA':
                print("CUDA device found.")
                cprefs.compute_device_type = 'CUDA'  # Use CUDA for NVIDIA GPUs
            elif cprefs.compute_device_type == 'OPTIX':
                print("Optix device found.")
                cprefs.compute_device_type = 'OPTIX'
            elif cprefs.compute_device_type == 'OPENCL':
                print("OpenCL device found.")
                cprefs.compute_device_type = 'OPENCL'  # Use OpenCL for AMD GPUs
            elif cprefs.compute_device_type == 'METAL':
                print("Metal device found.")
                cprefs.compute_device_type = 'METAL'
            else:
                print("No valid GPU compute device found.")
                return

            # Enable all available devices (either CUDA or OpenCL)
            for device in cprefs.devices:
                if device.type == cprefs.compute_device_type:
                    device.use = True
                else:
                    device.use = False
            print("GPU devices enabled.")
            print("Available devices:")

        except Exception as e:
            print(f"Error configuring GPU devices: {e}")
    else:
        print("Configuring render settings for CPU...")
        scene.cycles.device = 'CPU'
        print("scene.cycles.device", scene.cycles.device)

        try:
            total_threads = multiprocessing.cpu_count()
            scene.render.threads_mode = 'FIXED'
            scene.render.threads = int(total_threads * 0.9)
            print(f"Limiting CPU usage to {scene.render.threads} threads out of {total_threads}")
            prefs = bpy.context.preferences
            cprefs = prefs.addons["cycles"].preferences
            cprefs.compute_device_type = 'NONE'
            print("cprefs compute device", cprefs.compute_device_type)
            # Disable all GPU devices and set compute device type to NONE
            for device in cprefs.devices:
                if device.type in {'CUDA', 'OPTIX', 'OPENCL', 'ONEAPI'}:
                    device.use = False
                    print(f"Disabled GPU device: {device.name}")
            print("GPU devices disabled.")
        except Exception as e:
            print(f"Error disabling GPU devices: {e}")
        # Print the final device settings

    print("Final device settings:")
    for device in cprefs.devices:
        print(f" - {device.name} (Type: {device.type}, Use: {device.use})")

def main():
    """
    Main execution function:
      1. Parses command-line arguments.
      2. Configures the render device.
      3. Initiates the render.
      4. Exits Blender after a brief pause.
    """
    args = parse_args()
    render_mode = args.get("render_mode", "cpu")
    print(f"Render mode selected: {render_mode}")

    configure_render_device(render_mode)

    # Optionally adjust additional render settings here:
    # e.g., output file paths, resolution, samples, etc.
    #bpy.context.scene.render.filepath = r"C:/Users/Scott/Documents/SSE-group3-project1/results/render_output.png"

    # print("scene device: ", bpy.context.scene.device)
    print("Starting render...")
    bpy.ops.render.render(write_still=False)
    print("Render completed.")

    # Ensure Blender exits properly on Windows
    time.sleep(2)
    bpy.ops.wm.quit_blender()

if __name__ == "__main__":
    main()
