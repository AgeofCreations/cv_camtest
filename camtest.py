import logging
import sys

from cv2 import cv2 as cv
import requests
from datetime import datetime
from multiprocessing import Process, freeze_support
from functools import partial
from signal import signal, SIGUSR1, SIGUSR2
# from tmp.room import room

logger = logging.getLogger(__name__)


def change_res(cam, width, height):
    cam.set(3, width)
    cam.set(4, height)


class CameraControls(object):
    def __init__(self):
        self.flag = True

    def recording(self):
        # out = cv.VideoWriter(f'{room}.avi', fourcc, 10.0, size, 1)
        cam = cv.VideoCapture(0)  # 0 -> index of camera
        width = int(cam.get(cv.CAP_PROP_FRAME_WIDTH) + 0.5)
        height = int(cam.get(cv.CAP_PROP_FRAME_HEIGHT) + 0.5)
        change_res(cam, width, height)
        size = (width, height)
        # Define the codec and create VideoWriter object
        fourcc = cv.VideoWriter_fourcc(*'XVID')
        out = cv.VideoWriter(f'output.avi', fourcc, 24.0, size, 1)
        while True:
            ret, frame = cam.read()
            out.write(frame)

            if not self.flag:
                cam.release()
                out.release()
                cv.destroyAllWindows()
                break

    def stop_signal_handler(self, signum, frame):
        logger.debug("Got SIGUSR1")
        self.flag = False


async def read_and_send_vid(barcode, auth_token):
    name = f"{barcode}-{str(datetime.today().timestamp()).split('.')[0]}"
    url = f"http://se.sima-land.local/swift/v1/alcotest_vid/{name}.avi"
    head = {
        "X-Auth-Token": auth_token,
        "Content-Type": "video/x-msvideo",
    }
    with open('output.avi', mode='rb') as file:
        logger.debug("file opened")
        response = requests.put(url=url, headers=head, files={"file": file.read()})
        logger.debug(f"Auth_token: {auth_token}")
        if response.status_code == 201:
            logger.debug(f"Vid sent: {name}")
            return name
        else:
            logger.debug(f"Vid not sent status code: {response.status_code}| {response.content}")
            return "Error"

cl1 = CameraControls()


def start_proc():
    p = Process(target=cl1.recording)
    p.start()
    recording_pid = p.pid
    logger.debug(f"PID: {recording_pid}")
    signal(SIGUSR1, cl1.stop_signal_handler)
    return recording_pid


