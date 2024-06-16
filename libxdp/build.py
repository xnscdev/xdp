import libxdp

import certifi
from contextlib import contextmanager
from humanize import naturalsize
from io import BytesIO
import os
import pycurl
import subprocess
import tarfile
import tempfile
import toml
from urllib.parse import urlparse
import zipfile

@contextmanager
def cwd(path):
    old = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)

def download_progress(download_total, download_done, upload_total, upload_done):
    if not download_total:
        return
    s = 'Downloading sources... %s/%s' % (
        naturalsize(download_done, gnu=True),
        naturalsize(download_total, gnu=True)
    )
    print(s.ljust(os.get_terminal_size().columns), end='\r')

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
                d = scope['deps'](package.options(), package.dep_map)
                libxdp.process_deps(package, d)
            except KeyError:
                pass

        package.build_script = z.read('build.py').decode('utf-8')

def install_package(package):
    pstr = f'{package.name}-{package.version}'
    libxdp.update_action('Preparing', pstr)
    with tempfile.TemporaryDirectory() as dirname:
        archive_url = os.path.basename(urlparse(package.url).path)
        archive_name = dirname + '/' + archive_url
        with open(archive_name, 'wb') as archive:
            c = pycurl.Curl()
            c.setopt(c.URL, package.url)
            c.setopt(c.WRITEDATA, archive)
            c.setopt(c.CAINFO, certifi.where())
            c.setopt(c.NOPROGRESS, False)
            c.setopt(c.XFERINFOFUNCTION, download_progress)
            try:
                c.perform()
            except:
                libxdp.error('Failed to download archive at ' + package.url)
                c.close()
                exit(1)
            else:
                c.close()
        print()

        with tarfile.open(archive_name, 'r') as tar:
            tar.extractall(path=dirname)

        with cwd(archive_name[:archive_name.index('.tar')]):
            scope = {}
            exec(package.build_script, scope)
            libxdp.update_action('Building', pstr)
            try:
                scope['build'](package.options())
            except subprocess.CalledProcessError:
                libxdp.error('Build process exited with non-zero status')
                exit(1)

            libxdp.update_action('Installing', pstr)
            try:
                scope['install'](package.options())
            except subprocess.CalledProcessError:
                libxdp.error('Install process exited with non-zero status')
                exit(1)

        libxdp.update_installed(package)
        libxdp.update_action('Finished', 'installing ' + pstr)
