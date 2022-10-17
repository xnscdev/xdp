import libxdp

__package_order = []

def process_package(package):
    libxdp.load_xbuild(package)
    __package_order.append(package)

def process_deps(package, deps):
    for d in deps:
        good = False
        for p in __package_order:
            if p.name == d:
                good = True
                break
        if not good:
            parts = d.split()
            if len(parts) > 1:
                options = parts[2]
            else:
                options = ''
            try:
                offset = d.find(next(filter(lambda v: not v.isalnum(), d)))
                package = libxdp.find_package(d[:offset], d[offset:], options)
            except StopIteration:
                package = libxdp.find_package(d, '', options)
            if not package:
                libxdp.error('Failed to resolve dependency: ' + d)
                exit(1)
            __package_order.append(package)

def install_packages():
    for package in __package_order:
        libxdp.install_package(package)
