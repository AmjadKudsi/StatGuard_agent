import subprocess

def list_path():
    # High severity: user controlled input combined with shell=True
    cmd = "ls " + input("Enter path: ")
    subprocess.call(cmd, shell=True)
