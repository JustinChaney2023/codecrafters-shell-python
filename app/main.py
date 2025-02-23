import sys
import os

def main():
    while True:
        sys.stdout.write("$ ")

        # Wait for user input
        command = input().strip()
        if command.startswith("exit"):
            exit(command[5:].strip())
        elif command.startswith("echo"):
            echo(command[5:].strip())
        elif command.startswith("type"):
            print(type(command[5:].strip()))
        else:
            print(f"{command}: command not found")

def exit(code):
    try:
        sys.exit(int(code)) # Converts string to integer to take exit code
    except ValueError:
        sys.exit(0)         # Defaults to 0 if no integer is provided

def echo(text):             # Prints text taken after echo command
    print(text)

def type(command):          # Gives command type
    builtins = ["echo", "exit"]

    if command in builtins:
        return f"{command} is a shell builtin"
    else:
        return f"{command}: not found"


if __name__ == "__main__":
    main()
