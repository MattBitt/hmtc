# didn't really get this to work, but maybe something helpful below.

import asyncio

import vlc_controller


async def main():
    vlc = vlc_controller.VlcInstance()  # Create object
    await vlc.open_vlc(host="localhost", port=46500)  # Open VLC and connect to it
    await vlc.play("/home/matt/music/v2131282659.mp4")  # Play file
    # await vlc.pause()  # Toggle pause
    await vlc.send_command("seek 10")  # Send command to vlc
    await vlc.quit()  # Stop playing and close VLC


if __name__ == "__main__":
    asyncio.run(main())


import asyncio
import os
import signal
# for finding free ports
import socket
from random import randint

"""
┌──────────────────────────────────────────────────────────────────────────┐
│ Script that controls vlc client asynchronously via remote control socket │
│ Requires VLC media player  https://www.videolan.org/vlc/                 │
└──────────────────────────────────────────────────────────────────────────┘
"""
# use this command to star the server
# vlc --intf rc --rc-host 127.0.0.1:44500
DEBUG = False


# gets random free port
def get_free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        port = randint(49152, 65535)  # get random port number (from private port range)
        if s.connect_ex(("localhost", port)) != 0:
            break
    return port


class VlcInstance:
    def __init__(self, bin_path: str = os.getcwd()):
        self.bin_path = (
            bin_path  # path to vlc executable directory (use ./ if vlc is in PATH)
        )

        # async socket objects
        self.reader = None
        self.writer = None

        self.output_history = []  # history of output
        self.vlc_process = None  # holds Popen object of vlc process

        self.now_playing = None  # name of currently playing file

    async def open_vlc(
        self, host: str = "localhost", port: int = get_free_port()
    ) -> None:

        if self.writer is not None:  # if socket is already opened
            Exception("vlc is already opened")
            return

        # open vlc player
        tmp_path = os.getcwd()  # get current working directory
        os.chdir(self.bin_path)
        # self.vlc_process = Popen(
        #     f"vlc --extraintf rc --rc-host {host}:{port}".split(" ")
        # )
        os.chdir(tmp_path)  # return to previous working directory

        # connect to vlc player
        self.reader, self.writer = await asyncio.open_connection(host, port)
        if DEBUG:
            print(f"connected to {host}:{port}")

    # close vlc player and quit
    async def quit(self) -> None:
        os.kill(self.vlc_process.pid, signal.SIGTERM)  # kill vlc process
        self.vlc_process.wait()  # and wait for it to finish
        self.writer.close()  # close socket connection
        self.reader, self.writer = None, None
        self.now_playing = None
        if DEBUG:
            print("closed vlc player")

    # send command to vlc player
    async def send_command(self, command: str, clear_output: bool = True) -> list:
        """use help command to get list of available commands"""
        if self.writer is None:  # check if vlc is opened
            Exception("vlc is not opened")
            return []

        if clear_output:
            await self.read_output()  # clear output before sending command
        self.writer.write(f"{command}\n".encode("utf-8"))
        await self.writer.drain()
        if DEBUG:
            print(f"sent: {command}")
        return await self.read_output()  # return response to command

    # read all the output
    async def read_output(self) -> list:
        recived = []
        while True:  # read all the output
            try:
                recived.append(
                    await asyncio.wait_for(self.reader.readline(), timeout=1)
                )
            except asyncio.TimeoutError:
                break

        response = [row.decode("utf-8") for row in recived]  # decode output
        if len(response) > 0 and DEBUG:  # print response if there is any
            print("".join(response))
        self.output_history += response
        return response

    # play selected file
    async def play(self, path_to_file: str) -> None:
        self.now_playing = path_to_file.split("\\")[-1]  # get file name from path
        await self.send_command("clear")  # clear the queue
        await self.send_command(f"add {path_to_file}")  # add file to queue

    # toggle play/pause
    async def pause(self) -> None:
        await self.send_command("pause")
