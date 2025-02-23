import sys
import os
import subprocess

def main():
    while True:
        sys.stdout.write("$ ")

        # Wait for user input
        command = input().strip()
        if not command:
            continue

        if command.startswith("exit"):
            exit(command[5:].strip())
        elif command.startswith("echo"):
            echo(command[5:].strip())
        elif command.startswith("type"):
            print(type_command(command[5:].strip()))
        else:
            execute_command(command)

def exit(code):
    try:
        sys.exit(int(code)) # Converts string to integer to take exit code
    except ValueError:
        sys.exit(0)         # Defaults to 0 if no integer is provided

def echo(text):             # Prints text taken after echo command
    print(text)

def type_command(command):  # Gives command type
    builtins = ["echo", "exit", "type"]

    if command in builtins:
        return f"{command} is a shell builtin"

    # Get PATH directories
    path_dirs = os.environ.get("PATH", "").split(":")

    for directory in path_dirs:
        full_path = os.path.join(directory, command)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):  # Check if executable
            return f"{command} is {full_path}"

    return f"{command}: not found"

def execute_command(command_input):
    # Searches for an executable in PATH and runs it with arguments
    parts = command_input.split()
    command = parts[0]
    args = parts[1:]  # Extract arguments

    path_dirs = os.environ.get("PATH", "").split(":")
    
    for directory in path_dirs:
        full_path = os.path.join(directory, command)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            try:
                subprocess.run([full_path] + args)
                return
            except Exception as e:
                print(f"Error executing {command}: {e}")
                return

    print(f"{command}: command not found")

if __name__ == "__main__":
    main()
