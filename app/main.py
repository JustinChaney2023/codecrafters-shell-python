import sys
import os
import subprocess
import shlex

def main():
    while True:
        sys.stdout.write("$ ")

        # Wait for user input
        command_input = input().strip()
        if not command_input:
            continue

        parts = shlex.split(command_input, posix=True)  # Ensure arguments are parsed correctly
        command = parts[0]
        args = parts[1:]

        if command.startswith("exit"):
            exit(args)
        elif command.startswith("echo"):
            echo(args)
        elif command.startswith("type"):
            if args:
                print(type_command(args[0]))
            else:
                print("type: missing argument")
        elif command.startswith("pwd"):
            pwd()
        elif command.startswith("cd"):
            if args:
                cd(args[0])
            else:
                cd("~")                         # Default to home if no argument is provided
        else:
            execute_command(command, args)

def exit(args):
    """Exit the shell with an optional exit code"""
    try:
        sys.exit(int(args[0]) if args else 0)   # Converts string to integer to take exit code
    except ValueError:
        sys.exit(0)                             # Defaults to 0 if no integer is provided

def echo(args):                                 # Prints text taken after echo command
    """Prints the provided arguments as a single line"""
    print(" ".join(args))

def pwd():                                      # Prints current working directory
    """Prints current working directory"""
    print(os.getcwd())

def cd(directory):                              # Changes current working directory
    """Changes current working directory"""
    if directory == "~":                        # Changes to home directory
        homepath = os.path.expanduser("~")
        os.chdir(homepath)
        return

    try:
        os.chdir(directory)
    except FileNotFoundError:
        print(f"cd: {directory}: No such file or directory")
    except PermissionError:
        print(f"cd: {directory}: Permission denied")
    except Exception as e:
        print(f"cd: {directory}: {e}")

def type_command(command):  # Gives command type
    """Determines if the command is a builtin or an executable"""
    builtins = ["echo", "exit", "type", "pwd"]

    if command in builtins:
        return f"{command} is a shell builtin"

    # Get PATH directories
    path_dirs = os.environ.get("PATH", "").split(":")

    for directory in path_dirs:
        full_path = os.path.join(directory, command)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):  # Check if executable
            return f"{command} is {full_path}"

    return f"{command}: not found"

def execute_command(command, args):
    """Searches for an executable in PATH and runs it with arguments"""
    path_dirs = os.environ.get("PATH", "").split(":")
    
    for directory in path_dirs:
        full_path = os.path.join(directory, command)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            try:
                subprocess.run([command] + args, executable=full_path)
                return
            except Exception as e:
                print(f"Error executing {command}: {e}")
                return

    print(f"{command}: command not found")

if __name__ == "__main__":
    main()
