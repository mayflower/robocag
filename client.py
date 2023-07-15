# -*- coding: utf-8 -*-
import io
import cv2
import copy
import socket
import struct
import threading
from PID import *
import numpy as np
from Thread import *
from PIL import Image
from Command import COMMAND as cmd


class Client:
    def __init__(self):
        self.pid = Incremental_PID(1, 0, 0.0025)
        self.tcp_flag = False
        self.video_flag = True
        self.ball_flag = False
        self.face_flag = False
        self.face_id = False
        self.image = ""
        self.move_speed = "4"
        self.sonic: int = 0
        self.power: float = 0
        self.relax: bool = False
        self.ip = ""

    def turn_on_client(self, ip):
        self.client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.instruction = threading.Thread(target=self.receive_instruction, args=(ip,))
        self.instruction.start()
        self.ip = ip
        print("Connecttion to ", ip, " successful !")

    def receive_instruction(self, ip):
        try:
            self.client_socket1.connect((ip, 5001))
            self.tcp_flag = True
            print("Connecttion Successful !")
        except Exception as e:
            print("Connect to server Failed!: Server IP is right? Server is opened?")
            self.tcp_flag = False
        while True:
            try:
                alldata = self.receive_data()
            except:
                self.tcp_flag = False
                break
            if alldata == "":
                break
            else:
                cmdArray = alldata.split("\n")
                if cmdArray[-1] != "":
                    cmdArray == cmdArray[:-1]
            for oneCmd in cmdArray:
                data = oneCmd.split("#")
                if data == "":
                    self.tcp_flag = False
                    break
                elif data[0] == cmd.CMD_SONIC:
                    self.sonic = int(data[1])
                elif data[0] == cmd.CMD_POWER:
                    if data[1] != "":
                        power_value = round((float(data[1]) - 7.00) / 1.40 * 100)
                        self.power = power_value
                elif data[0] == cmd.CMD_RELAX:
                    if data[1] == "0":
                        self.relax = False
                    else:
                        self.relax = True

    def turn_off_client(self):
        try:
            self.client_socket.shutdown(2)
            self.client_socket1.shutdown(2)
            self.client_socket.close()
            self.client_socket1.close()
            stop_thread(self.instruction)
        except Exception as e:
            print(e)

    def is_valid_image_4_bytes(self, buf):
        bValid = True
        if buf[6:10] in (b"JFIF", b"Exif"):
            if not buf.rstrip(b"\0\r\n").endswith(b"\xff\xd9"):
                bValid = False
        else:
            try:
                Image.open(io.BytesIO(buf)).verify()
            except:
                bValid = False
        print("Image is valid ", bValid)
        return bValid

    def get_image(self):
        print("getting image")
        self.receiving_video(self.ip)
        print("got image")
        return self.image.copy()

    def get_sonic(self):
        command = cmd.CMD_SONIC + "\n"
        self.send_data(command)

    def turn_left(self):
        command = cmd.CMD_TURN_LEFT + "#" + self.move_speed + "\n"
        self.send_data(command)
        return "I turned left"

    def turn_right(self):
        command = cmd.CMD_TURN_RIGHT + "#" + self.move_speed + "\n"
        self.send_data(command)
        return "I turned right"

    def move_forward(self):
        command = cmd.CMD_MOVE_FORWARD + "#" + self.move_speed + "\n"
        self.send_data(command)
        return "I moved forward"

    def move_backward(self):
        command = cmd.CMD_MOVE_BACKWARD + "#" + self.move_speed + "\n"
        self.send_data(command)
        return "I moved backward"

    def move_stop(self):
        command = cmd.CMD_MOVE_STOP + "#" + self.move_speed + "\n"
        self.send_data(command)
        return "I stopped"

    def receiving_video(self, ip):
        done = False
        stream_bytes = b" "
        try:
            self.client_socket.connect((ip, 8001))
            self.connection = self.client_socket.makefile("rb")
        except:
            # print ("command port connect failed")
            pass
        while not done:
            try:
                print("receiving video")
                stream_bytes = self.connection.read(4)
                leng = struct.unpack("<L", stream_bytes[:4])
                jpg = self.connection.read(leng[0])
                if self.is_valid_image_4_bytes(jpg):
                    if self.video_flag:
                        self.image = cv2.imdecode(
                            np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR
                        )
                        self.video_flag = False
                        done = True
            except BaseException as e:
                print(e)
                break

    def send_data(self, data):
        if self.tcp_flag:
            try:
                self.client_socket1.send(data.encode("utf-8"))
            except Exception as e:
                print(e)

    def receive_data(self):
        data = ""
        data = self.client_socket1.recv(1024).decode("utf-8")
        return data


if __name__ == "__main__":
    pass
