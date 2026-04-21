import os
import signal
pid = os.getpid()
os.kill(pid, signal.SIGTERM)