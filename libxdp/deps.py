import libxdp

__package_order = []
__circular_dep_stack = set()

def process_package(package):
    libxdp.load_xbuild(package)
    __package_order.append(package)

def process_deps(parent, deps):
    if parent.name in __circular_dep_stack:
        libxdp.error('Circular dependency chain detected: ' + parent.name +
                     ' is already required by another package')
        exit(1)
    __circular_dep_stack.add(parent.name)
    for d in deps:
        good = False
        for p in __package_order:
            if p.name == d:
                good = True
                break
        if good:
            continue

        parts = d.split()
        if len(parts) > 1:
            options = parts[2]
        else:
            options = ''
        try:
            offset = d.find(next(filter(lambda v: not v.isalnum(), d)))
            name = d[:offset]
            version_str = d[offset:]
        except StopIteration:
            name = d
            version_str = ''

        package = libxdp.find_package(name, version_str, options)
        if not package:
            libxdp.error('Failed to resolve dependency: ' + d)
            exit(1)

        if libxdp.package_installed(package):
            continue

        libxdp.load_xbuild(package)
        __package_order.append(package)
    __circular_dep_stack.remove(parent.name)

def install_packages():
    for package in __package_order:
        libxdp.install_package(package)
