import os
import importlib.util

MODULES_DIR = "modules"

def load_and_run_modules():
    for filename in os.listdir(MODULES_DIR):
        if filename.endswith(".py"):
            module_path = os.path.join(MODULES_DIR, filename)
            module_name = filename[:-3]  

            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "run"):
                print(f"{module_name} çalışdırılır...")
                module.run()  

if __name__ == "__main__":
    load_and_run_modules()