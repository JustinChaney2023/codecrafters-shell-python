import sys
import os

def main():
    while True:
        sys.stdout.write("$ ")

        # Wait for user input
        command = input().strip()
        if command.startswith("exit"):
            break
        elif command.startswith("echo"):
            echo(command[5:].strip())
        else:
            print(f"{command}: command not found")

def echo(text):
    print(text)

if __name__ == "__main__":
    main()
