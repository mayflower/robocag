# -*- coding: utf-8 -*-
import io
import copy
import socket
import struct
import threading
import numpy as np
from Thread import *
from PIL import Image


class Client:
    def __init__(self):
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
        print("Connection to ", ip, " successful !")

    def receive_instruction(self, ip):
        pass

    def turn_off_client(self):
        print("Client is off")

    def get_image(self):
        print("get image")
        self.image = Image.open("fake_image.jpg")
        return self.image

    def get_sonic(self):
        self.sonic = 100  # fake sonic
        return self.sonic

    def turn_left(self):
        print("I turned left")
        return "I turned left"

    def turn_right(self):
        print("I turned right")
        return "I turned right"

    def move_forward(self):
        print("I moved forward")
        return "I moved forward"

    def move_backward(self):
        print("I moved backward")
        return "I moved backward"

    def move_stop(self):
        print("I stopped")
        return "I stopped"


if __name__ == "__main__":
    pass
