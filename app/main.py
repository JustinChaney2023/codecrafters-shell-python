import sys
import os
import subprocess
import shlex

def main():
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()

        # Wait for user input
        command_input = input().strip()
        if not command_input:
            continue

        # Check for output redirection (>)
        output_file = None
        parts = shlex.split(command_input, posix=True)

        if ">" in parts or "1>" in parts:
            try:
                if ">" in parts:
                    idx = parts.index(">")
                else:
                    idx = parts.index("1>")

                if idx + 1 >= len(parts):
                    print("syntax error: expected filename after '>'")
                    continue  # Prevents infinite loop if no file is provided

                output_file = parts[idx + 1]  # Extract filename
                parts = parts[:idx]  # Remove redirection part from command

            except IndexError:
                print("syntax error: unexpected token '>'")
                continue  # Prevents the loop from getting stuck

        if not parts:  # Ensure valid command exists after removing redirection
            continue  

        command = parts[0]
        args = parts[1:]

        if command == "exit":
            exit(args)
        elif command == "echo":
            echo(args, output_file)  
        elif command == "type":
            if args:
                execute_type(args[0], output_file)
            else:
                execute_type("missing argument", output_file)
        elif command == "pwd":
            execute_pwd(output_file)
        elif command == "cd":
            if args:
                cd(args[0])
            else:
                cd("~")  
        else:
            execute_command(command, args, output_file)

def exit(args):
    """Exit the shell with an optional exit code"""
    try:
        sys.exit(int(args[0]) if args else 0)   # Converts string to integer to take exit code
    except ValueError:
        sys.exit(0)                             # Defaults to 0 if no integer is provided

def echo(args, output_file=None):
    """Prints the provided arguments as a single line, with optional redirection"""
    output = " ".join(args)
    if output_file:
        with open(output_file, "w") as f:
            f.write(output + "\n")
    else:
        print(output)

def execute_pwd(output_file=None):
    """Prints current working directory, with optional redirection"""
    output = os.getcwd()
    if output_file:
        with open(output_file, "w") as f:
            f.write(output + "\n")
    else:
        print(output)

def cd(directory):
    """Changes current working directory"""
    if directory == "~":
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

def execute_type(command, output_file=None):
    """Determines if the command is a builtin or an executable"""
    builtins = ["echo", "exit", "type", "pwd", "cd"]

    if command in builtins:
        output = f"{command} is a shell builtin"
    else:
        path_dirs = os.environ.get("PATH", "").split(":")
        output = f"{command}: not found"
        for directory in path_dirs:
            full_path = os.path.join(directory, command)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                output = f"{command} is {full_path}"
                break

    if output_file:
        with open(output_file, "w") as f:
            f.write(output + "\n")
    else:
        print(output)

def execute_command(command, args, output_file=None):
    """Searches for an executable in PATH and runs it with arguments, supporting output redirection"""
    path_dirs = os.environ.get("PATH", "").split(":")

    for directory in path_dirs:
        full_path = os.path.join(directory, command)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            try:
                # Open file only if redirection is requested
                if output_file:
                    with open(output_file, "w") as f:
                        subprocess.run([full_path] + args, stdout=f, stderr=sys.stderr)  # Fix: Ensures errors print in terminal

                else:
                    subprocess.run([full_path] + args)  # No redirection, normal execution
                
                return
            except Exception as e:
                print(f"Error executing {command}: {e}")
                return

    print(f"{command}: command not found")


if __name__ == "__main__":
    main()
