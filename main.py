import os

import camtest
import time
from signal import SIGUSR1


if __name__ == '__main__':
    cam_pid = camtest.start_proc()

    time.sleep(10)

    os.kill(cam_pid, SIGUSR1)
