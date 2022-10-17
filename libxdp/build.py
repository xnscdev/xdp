import libxdp

import certifi
from io import BytesIO
import pycurl
import subprocess
import toml
import zipfile

def load_xbuild(package):
    bytes = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, package.xbuild)
    c.setopt(c.WRITEDATA, bytes)
    c.setopt(c.CAINFO, certifi.where())
    try:
        c.perform()
    except:
        libxdp.error('Failed to download XBUILD file from ' + package.xbuild)
        c.close()
        exit(1)
    else:
        c.close()

    with zipfile.ZipFile(bytes, 'r', zipfile.ZIP_DEFLATED, False) as z:
        meta = toml.loads(z.read('meta.toml').decode('utf-8'))
        if meta['api'] > libxdp.__api:
            libxdp.error('Package API version exceeds maximum supported ' +
                         'version by this version of XDP, please update XDP')
            exit(1)
        if 'deps' in meta:
            libxdp.process_deps(package, meta['deps'])
        else:
            try:
                deps_script = z.read('deps.py').decode('utf-8')
                scope = {}
                exec(deps_script, scope)
                d = scope['deps'](package.options)
                libxdp.process_deps(package, d)
            except KeyError:
                pass

def install_package(package):
    print(f'Installing {package.name}-{package.version}')
