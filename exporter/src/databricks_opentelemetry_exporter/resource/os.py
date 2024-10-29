import socket
import platform

# Get the hostname
HOST_NAME = socket.gethostname()

def get_os_info():
    try:
        with open('/etc/os-release', 'r') as f:
            lines = f.readlines()
        info = dict(line.strip().split('=', 1) for line in lines if '=' in line)
        return info.get('NAME', '').strip('"'), info.get('VERSION', '').strip('"'), info.get('VERSION_CODENAME', '').strip('"')
    except:
        return '', '', ''

name, version, codename = get_os_info()
OS_DESCRIPTION = f"{name} {version} {codename}".strip()
OS_NAME = name.lower() if name else platform.system().lower()
OS_TYPE = platform.system().lower()

