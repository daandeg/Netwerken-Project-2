from bTCP_client import *
from bTCP_server import *
import _thread

_thread.start_new_thread(shandshake, ())
_thread.start_new_thread(chandshake, ())
