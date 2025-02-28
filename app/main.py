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

        # Check for output redirection (> or 1>)
        output_file = None
        append_output = False
        error_file = None
        parts = shlex.split(command_input, posix=True)

        # Handle stderr redirection (2>)
        if "2>" in parts:
            try:
                idx = parts.index("2>")
                if idx + 1 >= len(parts):
                    print("syntax error: expected filename after '2>'")
                    continue  # Prevents infinite loop if no file is provided

                error_file = parts[idx + 1]  # Extract stderr filename
                parts = parts[:idx]  # Remove redirection part from command

            except IndexError:
                print("syntax error: unexpected token '2>'")
                continue

        # Handle stdout redirection (> or 1>)
        if ">>" in parts or "1>>" in parts:
            try:
                if ">>" in parts:
                    idx = parts.index(">>")
                else:
                    idx = parts.index("1>>")

                if idx + 1 >= len(parts):
                    print("syntax error: expected filename after '>>'")
                    continue

                output_file = parts[idx + 1]  # Extract stdout filename
                append_output = True # Set append mode
                parts = parts[:idx]  # Remove redirection part from command

            except IndexError:
                print("syntax error: unexpected token '>>'")
                continue

        elif ">" in parts or "1>" in parts:
            try:
                if ">" in parts:
                    idx = parts.index(">")
                else:
                    idx = parts.index("1>")

                if idx + 1 >= len(parts):
                    print("syntax error: expected filename after '>'")
                    continue

                output_file = parts[idx + 1]  # Extract stdout filename
                append_output = False # Overwrite mode
                parts = parts[:idx]  # Remove redirection part from command

            except IndexError:
                print("syntax error: unexpected token '>'")
                continue

        if not parts:
            continue  # Ensure valid command exists

        command = parts[0]
        args = parts[1:]

        if command == "exit":
            exit(args)
        elif command == "echo":
            echo(args, output_file, error_file, append_output)  # Pass error_file to echo
        elif command == "type":
            if args:
                execute_type(args[0], output_file, append_output)
            else:
                execute_type("missing argument", output_file, append_output)
        elif command == "pwd":
            execute_pwd(output_file, append_output)
        elif command == "cd":
            if args:
                cd(args[0])
            else:
                cd("~")
        else:
            execute_command(command, args, output_file, error_file, append_output)


def exit(args):
    """Exit the shell with an optional exit code"""
    try:
        sys.exit(int(args[0]) if args else 0)   # Converts string to integer to take exit code
    except ValueError:
        sys.exit(0)                             # Defaults to 0 if no integer is provided

def echo(args, output_file=None, error_file=None, append_output=False):
    """Prints the provided arguments as a single line, with optional stdout and stderr redirection"""
    output = " ".join(args)

    # If stderr redirection (`2>`) is used, create an empty file
    if error_file:
        open(error_file, "w").close()  # Ensures the file exists (empty)
    
    # Redirect stdout if `>` is used
    if output_file:
        mode = "a" if append_output else "w" # Append mode if `>>`, otherwise overwrite
        with open(output_file, mode) as f:
            f.write(output + "\n")
    else:
        print(output)

def execute_pwd(output_file=None, append_output=False):
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

def execute_type(command, output_file=None, append_output=False):
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

def execute_command(command, args, output_file=None, error_file=None, append_output=False):
    """Searches for an executable in PATH and runs it with arguments, supporting output & error redirection"""
    path_dirs = os.environ.get("PATH", "").split(":")

    for directory in path_dirs:
        full_path = os.path.join(directory, command)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            try:
                stdout_target = open(output_file, "a" if append_output else "w") if output_file else None
                stderr_target = open(error_file, "a" if append_output else "w") if error_file else sys.stderr

                subprocess.run([command] + args, executable=full_path, stdout=stdout_target, stderr=stderr_target)

                if stdout_target:
                    stdout_target.close()
                if stderr_target and stderr_target is not sys.stderr:
                    stderr_target.close()

                return
            except Exception as e:
                print(f"Error executing {command}: {e}", file=sys.stderr)
                return

    print(f"{command}: command not found", file=sys.stderr)


if __name__ == "__main__":
    main()
