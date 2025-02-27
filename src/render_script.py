import bpy
import sys
import time
import multiprocessing

def parse_args():
    """
    Parse custom command-line arguments passed to Blender after the '--' separator.

    Returns:
        dict: A dictionary with key "render_mode" set to either "cpu" or "gpu",
              if provided. Otherwise default is {} empty dict.
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
    Configure the Cycles render device (CPU or GPU) for the given render mode.

    Args:
        render_mode (str): 'cpu' or 'gpu'
    """
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    print("Render engine set to:", scene.render.engine)

    prefs = bpy.context.preferences
    cprefs = prefs.addons["cycles"].preferences

    if render_mode == "gpu":
        print("Configuring render settings for GPU...")
        scene.cycles.device = 'GPU'
        
        try:
            # The compute_device_type might be 'CUDA', 'OPTIX', 'OPENCL', 'METAL', 'NONE', etc.
            if cprefs.compute_device_type in ('CUDA', 'OPTIX', 'OPENCL', 'METAL'):
                print(f"GPU device type found: {cprefs.compute_device_type}")
                cprefs.compute_device_type = cprefs.compute_device_type
            else:
                print("No valid GPU device found; falling back to CPU.")
                scene.cycles.device = 'CPU'
                cprefs.compute_device_type = 'NONE'
                return

            # Enable only devices matching the chosen compute_device_type
            for device in cprefs.devices:
                device.use = (device.type == cprefs.compute_device_type)
            
            print("GPU devices enabled.")
        except Exception as e:
            print(f"Error configuring GPU devices: {e}")
            # Fallback to CPU if GPU config fails
            scene.cycles.device = 'CPU'
            cprefs.compute_device_type = 'NONE'
    else:
        print("Configuring render settings for CPU...")
        scene.cycles.device = 'CPU'
        try:
            total_threads = multiprocessing.cpu_count()
            scene.render.threads_mode = 'FIXED'
            # Slightly reduce total threads if you want to leave some CPU overhead
            scene.render.threads = max(1, int(total_threads * 0.9))
            print(f"Limiting CPU usage to {scene.render.threads} threads out of {total_threads}")

            cprefs.compute_device_type = 'NONE'
            # Disable GPU devices
            for device in cprefs.devices:
                if device.type in {'CUDA', 'OPTIX', 'OPENCL', 'ONEAPI', 'METAL'}:
                    device.use = False
            print("All GPU devices disabled for CPU rendering.")
        except Exception as e:
            print(f"Error disabling GPU devices: {e}")

    print("Final device settings:")
    for device in cprefs.devices:
        print(f" - Name: {device.name}, Type: {device.type}, Use: {device.use}")

def main():
    """
    Main execution:
      1. Parse command-line arguments.
      2. Configure Cycles for CPU or GPU.
      3. Render a frame (without writing to disk by default).
      4. Exit Blender.
    """
    args = parse_args()
    render_mode = args.get("render_mode", "cpu")
    print(f"Selected render mode: {render_mode}")

    configure_render_device(render_mode)

    print("Starting render...")
    bpy.ops.render.render(write_still=False)
    print("Render completed.")

    # Pause to ensure log outputs are flushed and Blender has time to clean up
    time.sleep(2)
    bpy.ops.wm.quit_blender()

if __name__ == "__main__":
    main()