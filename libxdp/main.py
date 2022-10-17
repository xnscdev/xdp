import libxdp

import sys

def bad_usage():
    libxdp.error('Bad usage, try "xdp help"')
    exit(1)

def install(names):
    libxdp.load_packages()
    libxdp.load_options()
    packages = []
    error = False
    for name in names:
        package = libxdp.find_package(name)
        if not package:
            libxdp.error('No package found in repositories with name: ' + name)
            error = True
        packages.append(package)
    if error:
        exit(1)

    for package in packages:
        libxdp.process_package(package)
    libxdp.install_packages()

def main():
    if len(sys.argv) == 1:
        bad_usage()
    if sys.argv[1] == 'help':
        print('Usage: xdp help\n' +
              '       xdp sync\n' +
              '       xdp install PACKAGES...\n')
    elif sys.argv[1] == 'install':
        if len(sys.argv) == 2:
            libxdp.error('No packages to install')
            exit(1)
        install(sys.argv[2:])
    elif sys.argv[1] == 'sync':
        libxdp.sync_local()
    else:
        bad_usage()
