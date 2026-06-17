try:
    script_path = hou.parm('script_path').eval()
    if script_path:
        with open(script_path, "r") as file:
            script_code = file.read()
        
        code = compile(script_code, "script.py", "exec")
        namespace = {}
        exec(code, namespace)
        if "importLPE" in namespace:
            result = namespace["importLPE"](`chs("lights")`)  # Call the function
        else:
            raise KeyError("Function 'my_function' not found in the script")
    else:
        print("Please provide a valid path to the Python script.")
except Exception as e:
    print(f"Error executing the Python script: {e}")