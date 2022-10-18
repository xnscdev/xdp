import libxdp.pkg.build.base as pkg

import multiprocessing
import os

def make_jobs():
    return max(2, multiprocessing.cpu_count())

def curr_package_str():
    return os.path.basename(os.getcwd())
