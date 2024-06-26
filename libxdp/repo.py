import libxdp

import certifi
from io import BytesIO
import packaging.version
import pycurl

__packages = []
__installed_packages = []
__default_options = []
__options = {}

class Package:
    def __init__(self, name, version, url, xbuild):
        self.name = name
        self.version = packaging.version.parse(version)
        self.url = url
        self.xbuild = xbuild
        self.env_options = set()
        self.required_options = set()
        self.dep_map = {}
        self.build_script = ''

    def __eq__(self, other):
        if isinstance(other, Package):
            return self.name == other.name and self.version == other.version
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Package):
            if self.name < other.name:
                return True
            if self.name == other.name and self.version < other.version:
                return True
            return False
        return NotImplemented

    def options(self):
        return self.env_options.union(self.required_options)

    def req_option_data(self):
        return self.name, tuple(self.required_options)

class VersionConstraint:
    def __init__(self):
        pass

    def satisfies(v):
        return NotImplemented

class LessVersionConstraint(VersionConstraint):
    def __init__(self, max_version):
        self.max_version = packaging.version.parse(max_version)

    def satisfies(v):
        return v <= self.max_version

class EqualVersionConstraint(VersionConstraint):
    def __init__(self, version):
        self.version = packaging.version.parse(version)

    def satisfies(v):
        return v == self.version

class GreaterVersionConstraint(VersionConstraint):
    def __init__(self, min_version):
        self.min_version = packaging.version.parse(min_version)

    def satisfies(v):
        return v >= self.min_version

def load_options():
    global __default_options
    with open(libxdp.__etc + '/options') as f:
        for line in f:
            if not line.startswith('#'):
                line = line.split()
                if line[0] == '*':
                    __default_options = line[1].split(',')
                else:
                    __options[line[0]] = line[1].split(',')

def sync_local():
    with open(libxdp.__etc + '/repo') as f:
        packages = []
        for line in f:
            line = line.rstrip()
            repo = line + '/repo.xdp'
            if not line.startswith('#'):
                bytes = BytesIO()
                c = pycurl.Curl()
                c.setopt(c.URL, repo)
                c.setopt(c.WRITEDATA, bytes)
                c.setopt(c.CAINFO, certifi.where())
                try:
                    c.perform()
                except:
                    libxdp.warning('Failed to read repository ' + repo +
                                   ', skipping')
                    continue
                finally:
                    c.close()
                for p in bytes.getvalue().decode().splitlines():
                    name, version, url = p.split()
                    xbuild = '%s/%s-%s.xbuild' % (line, name, version)
                    package = Package(name, version, url, xbuild)
                    if package not in packages:
                        packages.append(package)
                print('Fetched package list from ' + repo)

    packages.sort()
    with open(libxdp.__var + '/packages', 'w') as f:
        for package in packages:
            f.write('%s\t%s\t%s\t%s\n' % (package.name, str(package.version),
                                          package.url, package.xbuild))
    print('Found ' + str(len(packages)) + ' packages')

def load_packages():
    with open(libxdp.__var + '/packages') as f:
        for line in f:
            name, version, url, xbuild = line.split()
            package = Package(name, version, url, xbuild)
            __packages.append(package)

def load_installed():
    with open(libxdp.__var + '/installed') as f:
        for line in f:
            parts = line.split()
            try:
                options = parts[2].split(',')
            except IndexError:
                options = []
            __installed_packages.append((parts[0], parts[1], options))

def write_installed():
    with open(libxdp.__var + '/installed', 'w') as f:
        for p in __installed_packages:
            f.write('%s\t%s\t%s\n' % (p[0], p[1], ','.join(p[2])))

def update_installed(package):
    for p in __installed_packages:
        if p[0] == package.name:
            p[1] = str(package.version)
            p[2] = package.required_options
            write_installed()
            return
    __installed_packages.append((package.name, package.version,
                                 package.required_options))
    write_installed()

def package_installed(package):
    for p in __installed_packages:
        if p[0] == package.name and p[1] == str(package.version):
            return set(package.required_options) <= set(p[2])
    return False

def consume_options(opts, options):
    for o in options:
        if not o:
            continue
        if o.startswith('-'):
            o = o[1:]
            if o in opts:
                opts.remove(o)
        else:
            opts.add(o)

def find_package(name, version_str='', options=''):
    constraints = []
    data = version_str.split(',')
    for item in data:
        if item.startswith('>='):
            constraints.append(GreaterVersionConstraint(item[2:].strip()))
        elif item.startswith('='):
            constraints.append(EqualVersionConstraint(item[2:].strip()))
        elif item.startswith('<='):
            constraints.append(LessVersionConstraint(item[2:].strip()))

    candidates = []
    for package in __packages:
        if package.name == name:
            valid = True
            for constraint in constraints:
                if not constraint.satisfies(package.version):
                    valid = False
                    break
            if not valid:
                continue
            candidates.append(package)

    if not candidates:
        return None
    package = max(candidates)
    opts = set(__default_options)
    try:
        consume_options(opts, __options[package.name])
    except KeyError:
        pass
    package.env_options = opts
    opts = set()
    consume_options(opts, options.split(','))
    package.required_options = opts
    return package
