import sys


def main():

    while True:
        sys.stdout.write("$ ")

        # Wait for user input
        command = input()
        if command == "exit":
            break
        else:
            print(f"{command}: command not found")


if __name__ == "__main__":
    main()
