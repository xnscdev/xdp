import libxdp

import certifi
from io import BytesIO
import packaging.version
import pycurl

class Package:
    def __init__(self, name, version, url):
        self.name = name
        self.version = packaging.version.parse(version)
        self.url = url

def sync_local():
    with open(libxdp.__etc + '/repo') as f:
        packages = []
        for line in f:
            if not line.startswith('#'):
                bytes = BytesIO()
                c = pycurl.Curl()
                c.setopt(c.URL, line.rstrip())
                c.setopt(c.WRITEDATA, bytes)
                c.setopt(c.CAINFO, certifi.where())
                try:
                    c.perform()
                except:
                    continue
                finally:
                    c.close()
                for p in bytes.getvalue().decode().splitlines():
                    name, version, url = p.split()
                    package = Package(name, version, url)
                    found = False
                    for i in range(len(packages)):
                        if packages[i].name == package.name:
                            if packages[i].version < package.version:
                                packages[i].version = package.version
                                packages[i].url = package.url
                            found = True
                            break
                    if not found:
                        packages.append(package)

    for package in packages:
        print(package.name, package.version, package.url)
