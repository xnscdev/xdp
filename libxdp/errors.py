import libxdp

from colorama import Fore, Style
import sys

def warning(msg):
    print(f'{Fore.YELLOW}{Style.BRIGHT}Warning{Style.RESET_ALL}  {msg}',
          file=sys.stderr)

def error(msg):
    print(f'{Fore.RED}{Style.BRIGHT}Error{Style.RESET_ALL}  {msg}',
          file=sys.stderr)
