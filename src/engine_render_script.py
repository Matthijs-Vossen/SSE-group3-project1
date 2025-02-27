import bpy
import sys
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
def parse_args():
    """
    Parse command-line arguments passed after the '--' separator.

    Expected argument:
      --render_mode=cpu   (or gpu)

    Returns:
        dict: A dictionary containing the parsed arguments.
    """
    logging.info("Parsing command-line arguments...")
    argv = sys.argv
    if "--" not in argv:
        return {}

    # Extract all custom arguments after the '--' separator.
    custom_args = argv[argv.index("--") + 1:]
    args = {}
    for arg in custom_args:
        if arg.startswith("--render_engine="):
            # Remove any whitespace and convert the mode to lowercase.
            args["render_engine"] = arg.split("=", 1)[1].strip().upper()
    return args

def configure_render_engine(engine_type: str, render_mode: str):
    available_engines = [e.identifier for e in bpy.context.scene.render.bl_rna.properties["engine"].enum_items]
    print("Available render engines:", available_engines)
    scene = bpy.context.scene
    scene.render.engine = engine_type
    print(f"scene.render.engine, {scene.render.engine}")

    if engine_type == 'CYCLES':
        scene = bpy.context.scene

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

    elif engine_type == 'BLENDER_EEVEE':
        print("Configuring render settings for Eevee...")
        scene.eevee.taa_render_samples = 16
        scene.eevee.use_ssr = False
        scene.eevee.use_bloom = False
        scene.eevee.use_motion_blur = False

    elif engine_type == 'BLENDER_WORKBENCH':
        scene.display.shading.light = 'STUDIO'
        scene.display.shading.show_cavity = True
        scene.display.shading.cavity_type = 'BOTH'
        scene.display.shading.curvature_ridge_factor = 1.0
        scene.display.shading.curvature_valley_factor = 1.0
        scene.display.shading.show_shadows = True
        scene.display.shading.shadow_intensity = 0.5
    else:
        print(f"Unsupported render engine: {engine_type}")
        return
    print(f"Render engine set to: {scene.render.engine}")
def main():
    """
    Main execution function:
      1. Parses command-line arguments.
      2. Configures the render engine.
      3. Initiates the render.
      4. Exits Blender after a brief pause.
    """
    logging.info("Starting render script...")
    args = parse_args()
    logging.info(f"Parsed arguments: {args}")
    render_engine = args.get("render_engine", "BLENDER_EEVEE")
    logging.info(f"Render engine selected: {render_engine}")

    configure_render_engine(render_engine, "gpu")
    logging.info("Starting render...")
    bpy.ops.render.render(write_still=False)
    logging.info("Render completed.")

    time.sleep(2)
    bpy.ops.wm.quit_blender()

if __name__ == "__main__":
    main()
