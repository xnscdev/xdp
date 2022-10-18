import libxdp.pkg.build.base as pkg

import subprocess

def i18n_check(options, flags):
    if 'i18n' not in options:
        flags.append('--disable-nls')

def build(flags):
    configure_cmd = ['./configure'] + flags
    print('Configuring with ' + ' '.join(configure_cmd))
    subprocess.run(configure_cmd, check=True)
    subprocess.run(['make', '-j', str(pkg.make_jobs())], check=True)

def install():
    subprocess.run(['make', 'install'], check=True)
