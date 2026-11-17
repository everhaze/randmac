import os
import shutil
import subprocess
import sys
import tempfile

bold_bright_blue = "\033[1;94m"
bold_blue = "\033[1;34m"
green = "\033[32m"
red = "\033[31m"
reset = "\033[0m"

menu = """
1. Randomize mac (burnt)
2. Randomize mac
3. Randomize mac (preserving vendor bytes)
4. Randomize vendor mac of same kind
5. Randomize vendor mac of any kind
6. Use custom mac
7. Show current mac
8. Search vendors
0. Restore permanent mac"""

path = f"{tempfile.gettempdir()}/interface.txt"

a = "> "


def network(interface: str, up: bool):
    if up:
        subprocess.run(["ip", "link", "set", interface, "up"], check=True)
    else:
        subprocess.run(["ip", "link", "set", interface, "down"], check=True)


def cleanup(interface: str):
    try:
        os.remove(path)
        print(f"{green}Cleaned up: {path}{reset}")
    except FileNotFoundError:
        print(f"{green}No file to clear.{reset}")
    network(interface, False)
    subprocess.run(["macchanger", "--permanent", interface], check=True)
    network(interface, True)


def randomize_burnt(interface: str):
    network(interface, False)
    subprocess.run(["macchanger", "-r", "-b", interface], check=True)
    network(interface, True)


def randomize(interface: str):
    network(interface, False)
    subprocess.run(["macchanger", "--random", interface], check=True)
    network(interface, True)


def randomize_preserve_vendor(interface: str):
    network(interface, False)
    subprocess.run(["macchanger", "-e", interface], check=True)
    network(interface, True)


def random_vendor_same(interface: str):
    network(interface, False)
    subprocess.run(["macchanger", "-a", interface], check=True)
    network(interface, True)


def random_vendor_diff(interface: str):
    network(interface, False)
    subprocess.run(["macchanger", "-A", interface], check=True)
    network(interface, True)


def custom_mac(interface: str, mac: str):
    network(interface, False)
    try:
        subprocess.run(["macchanger", "-m", mac, interface], check=True)
    finally:
        network(interface, True)


def show(interface: str):
    subprocess.run(["macchanger", "-s", interface], check=True)


def list_vendors(filter: str):
    if filter == "":
        subprocess.run(["macchanger", "-l"], check=True)
    else:
        subprocess.run(["macchanger", f"--list={filter}"], check=True)


def write_interface() -> str:
    print(f"{bold_bright_blue}Enter interface{reset}")
    interface = input(a)
    with open(path, "w") as f:
        f.write(interface)
        print(f"{green}Saved interface: {interface}{reset}")
    return interface


def check_dependencies():
    if shutil.which("macchanger") == None:
        print(f"{red}Missing dependency: macchanger{reset}")
        sys.exit(0)
    print(f"{green}Found dependencies.{reset}")


def main():
    check_dependencies()

    if os.geteuid() != 0:
        print(f"{red}Sudo required.{reset}")
        sys.exit(1)

    interface = ""

    try:
        with open(path) as f:
            file = f.read()
            if file != "":
                print(f"{bold_bright_blue}Use interface: {file}? y/n{reset}")
                ask = input(a)
                if ask == "y":
                    print(f"{green}Using interface: {file}{reset}")
                    interface = file
                elif ask == "n":
                    interface = write_interface()
                else:
                    print(f"{red}Invalid option.{reset}")
                    sys.exit(1)
    except OSError:
        print(f"{red}No previous interface found.{reset}")
        interface = write_interface()
    print(f"{bold_blue}{menu}{reset}")
    pick = input(a)
    try:
        match pick:
            case "0":
                cleanup(interface)
            case "1":
                randomize_burnt(interface)
            case "2":
                randomize(interface)
            case "3":
                randomize_preserve_vendor(interface)
            case "4":
                random_vendor_same(interface)
            case "5":
                random_vendor_diff(interface)
            case "6":
                print(f"{bold_bright_blue}Enter custom mac{reset}")
                mac = input(a)
                custom_mac(interface, mac)
            case "7":
                show(interface)
            case "8":
                print(f"{bold_bright_blue}Enter keywords (or leave empty){reset}")
                filter = input(a)
                list_vendors(filter)
            case _:
                print(f"{red}Invalid option.{reset}")
                sys.exit(1)
    except subprocess.CalledProcessError:
        print(f"{red}Subprocess failed.{reset}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
