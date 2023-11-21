# from RobodogClient.Client import Client
from PIL import Image
from RobodogClient.Command import COMMAND as cmd
import threading
from RobodogClient.Thread import stop_thread
from client import Client 
# 


client = Client()
client.turn_on_client("10.93.16.138")

input("Wait")
client.get_sonic()

input("Wait")

client.turn_off_client()