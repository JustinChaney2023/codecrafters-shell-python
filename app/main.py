import sys
import os
import subprocess
import shlex
import contextlib  # For redirecting output in built-in commands

def safe_open(filename, mode):
    """
    Open a file in the given mode, ensuring its parent directory exists.
    """
    parent = os.path.dirname(filename)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    return open(filename, mode)

def main():
    """
    Main loop of the shell. Reads user input, parses for redirection operators,
    and dispatches to built-in functions or external commands. Also makes sure to
    flush output so that the prompt appears correctly.
    """
    while True:
        # Print prompt and flush stdout immediately.
        sys.stdout.write("$ ")
        sys.stdout.flush()
        try:
            command_input = input().strip()
        except EOFError:
            # Exit gracefully on EOF.
            print()  # Print newline before exiting.
            break

        if not command_input:
            continue

        # Initialize redirection options.
        output_file = None
        append_output = False
        error_file = None
        append_error = False

        # Split command input into parts (honoring quotes).
        parts = shlex.split(command_input, posix=True)

        # --- Handle stderr redirection (append and overwrite) ---
        if "2>>" in parts:
            idx = parts.index("2>>")
            if idx + 1 >= len(parts):
                print("syntax error: expected filename after '2>>'")
                continue
            error_file = parts[idx + 1]
            append_error = True
            parts = parts[:idx]
        elif "2>" in parts:
            idx = parts.index("2>")
            if idx + 1 >= len(parts):
                print("syntax error: expected filename after '2>'")
                continue
            error_file = parts[idx + 1]
            append_error = False
            parts = parts[:idx]

        # --- Handle stdout redirection (append and overwrite) ---
        if ">>" in parts or "1>>" in parts:
            try:
                idx = parts.index(">>") if ">>" in parts else parts.index("1>>")
                if idx + 1 >= len(parts):
                    print("syntax error: expected filename after '>>'")
                    continue
                output_file = parts[idx + 1]
                append_output = True
                parts = parts[:idx]
            except IndexError:
                print("syntax error: unexpected token '>>'")
                continue
        elif ">" in parts or "1>" in parts:
            try:
                idx = parts.index(">") if ">" in parts else parts.index("1>")
                if idx + 1 >= len(parts):
                    print("syntax error: expected filename after '>'")
                    continue
                output_file = parts[idx + 1]
                append_output = False
                parts = parts[:idx]
            except IndexError:
                print("syntax error: unexpected token '>'")
                continue

        if not parts:
            continue  # No command left to execute.

        command = parts[0]
        args = parts[1:]

        # If the command is a built-in, use a redirection context.
        if command in ["exit", "echo", "type", "pwd", "cd"]:
            with contextlib.ExitStack() as stack:
                if output_file:
                    f_out = safe_open(output_file, "a" if append_output else "w")
                    stack.enter_context(f_out)
                    stack.enter_context(contextlib.redirect_stdout(f_out))
                if error_file:
                    f_err = safe_open(error_file, "a" if append_error else "w")
                    stack.enter_context(f_err)
                    stack.enter_context(contextlib.redirect_stderr(f_err))
                if command == "exit":
                    exit_shell(args)
                elif command == "echo":
                    echo(args)
                elif command == "type":
                    if args:
                        execute_type(args[0])
                    else:
                        execute_type("missing argument")
                elif command == "pwd":
                    execute_pwd()
                elif command == "cd":
                    if args:
                        cd(args[0])
                    else:
                        cd("~")
        else:
            # For external commands, call execute_command.
            execute_command(command, args, output_file, error_file, append_output, append_error)

        # Ensure stdout is flushed at the end of command execution so the prompt shows.
        sys.stdout.flush()

def exit_shell(args):
    """
    Exit the shell with an optional exit code.
    """
    try:
        sys.exit(int(args[0]) if args else 0)
    except ValueError:
        sys.exit(0)

def echo(args):
    """
    Built-in echo command: prints its arguments to stdout.
    """
    print(" ".join(args))

def execute_pwd():
    """
    Built-in pwd command: prints the current working directory.
    """
    print(os.getcwd())

def execute_type(command):
    """
    Built-in type command: indicates whether the given command is a shell builtin
    or an executable (if found in PATH).
    """
    builtins = ["echo", "exit", "type", "pwd", "cd"]
    if command in builtins:
        print(f"{command} is a shell builtin")
    else:
        path_dirs = os.environ.get("PATH", "").split(":")
        for directory in path_dirs:
            full_path = os.path.join(directory, command)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                print(f"{command} is {full_path}")
                return
        print(f"{command}: not found")

def cd(directory):
    """
    Built-in cd command: changes the current working directory.
    Supports '~' as a shortcut for the home directory.
    """
    if directory == "~":
        directory = os.path.expanduser("~")
    try:
        os.chdir(directory)
    except FileNotFoundError:
        print(f"cd: {directory}: No such file or directory", file=sys.stderr)
    except PermissionError:
        print(f"cd: {directory}: Permission denied", file=sys.stderr)
    except Exception as e:
        print(f"cd: {directory}: {e}", file=sys.stderr)

def execute_command(command, args, output_file=None, error_file=None, append_output=False, append_error=False):
    """
    Execute an external command by searching for it in the PATH.
    Redirects stdout and/or stderr if redirection is specified.
    If the command is not found, prints an error message.
    """
    path_dirs = os.environ.get("PATH", "").split(":")
    for directory in path_dirs:
        full_path = os.path.join(directory, command)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            try:
                stdout_target = safe_open(output_file, "a" if append_output else "w") if output_file else None
                stderr_target = safe_open(error_file, "a" if append_error else "w") if error_file else sys.stderr

                subprocess.run([command] + args, executable=full_path,
                               stdout=stdout_target, stderr=stderr_target)

                if stdout_target:
                    stdout_target.close()
                if stderr_target and stderr_target is not sys.stderr:
                    stderr_target.close()
                return
            except Exception as e:
                print(f"Error executing {command}: {e}", file=sys.stderr)
                return

    # If no executable was found, output error message.
    error_message = f"{command}: command not found\n"
    if error_file:
        mode = "a" if append_error else "w"
        with safe_open(error_file, mode) as f:
            f.write(error_message)
    else:
        # Print to stderr and flush stdout so that the prompt appears immediately.
        print(error_message, file=sys.stderr, end="")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
