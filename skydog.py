import langchain
import cv2
import torch
from PIL import Image
from time import sleep
from langchain.agents import Tool, AgentType, initialize_agent
from langchain.tools import HumanInputRun, tool
from langchain.chat_models import ChatOpenAI
from langchain.experimental.plan_and_execute import (
    PlanAndExecute,
    load_agent_executor,
    load_chat_planner,
)
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from termcolor import colored
from fake_client import Client
from ram.models import ram
from ram import inference_ram as inference
from ram import get_transform

MODEL = "gpt-4"

langchain.debug = True
llm = ChatOpenAI(temperature=0, model=MODEL)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
skynet = Client()
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# transform = get_transform(image_size=384)
# delete_tag_index = [127, 2961, 3351, 3265, 3338, 3355, 3359]
# model = ram(
#    pretrained="./pretrained/ram_swin_large_14m.pth", image_size=384, vit="swin_l"
# )
# model.eval()
# model = model.to(device)


# @tool("look_around", return_direct=True)
def look_around(task: str):
    """observe the environment"""
    print("looking around")
    # image = skynet.get_image()
    # image = transform(skynet.get_image()).unsqueeze(0).to(device)
    # res = inference(image, model)
    # print("I see: " + res[0] + " in front of me")
    return "I see: pillar | computer | table | person | laptop | man | office building | wall lamp | sit | job in front of me"


def turn_left(task: str):
    print("turning left")
    skynet.turn_left()
    sleep(7)
    stop()


def turn_right(task: str):
    print("turning right")
    skynet.turn_right()
    sleep(7)
    stop()


def move_forward(task: str):
    print("moving forward")
    skynet.move_forward()
    sleep(7)
    stop()


def move_backward(task: str):
    print("moving backward")
    skynet.move_backward()
    sleep(7)
    stop()


def sonic(task: str):
    skynet.get_sonic()
    sleep(1)
    if skynet.sonic < 20:
        return "There is an obstacle in front of me"
    else:
        return "There is no obstacle in front of me"


def stop():
    print("stopping")
    skynet.move_stop()


tools = [
    Tool.from_function(
        func=look_around,
        name="explore",
        description="useful for when you want to see what is around you",
    ),
    Tool.from_function(
        func=sonic,
        name="obstacle_check",
        description="useful if you want to check if anything is in front of you",
    ),
    Tool.from_function(
        func=turn_left,
        name="turn left",
        description="useful for when you turn left",
    ),
    Tool.from_function(
        func=turn_right,
        name="turn right",
        description="useful for when you turn right",
    ),
    Tool.from_function(
        func=move_forward,
        name="move forward",
        description="useful for when you move forward",
    ),
    Tool.from_function(
        func=move_backward,
        name="move backward",
        description="useful for when you move backward",
    ),
    HumanInputRun(),
]

systemprompt = """You are a dog that can look, listen, move and speak. 
Your Owner is a human that can give you commands.
Let's first understand the task and devise a plan to execute the task.
Please output the plan starting with the header 'Plan:' 
and then followed by a numbered list of steps. 
Please make the plan the minimum number of steps required 
to accurately complete the task. If the task is a question, 
the final step should almost always be 'Given the above steps taken, 
please fulfill your owners original command.'. 
At the end of your plan, say '<END_OF_PLAN>'

"""

planner = load_chat_planner(llm, system_prompt=systemprompt)
executor = load_agent_executor(llm, tools, verbose=True)
agent = PlanAndExecute(planner=planner, executor=executor, verbose=True)


def run():
    skynet.turn_on_client("skynet")
    sleep(3)
    print(colored("Hello, i am RoboDog. What can i do for you?", "green"))
    try:
        while True:
            query = input(colored("You: ", "white", attrs=["bold"]))
            result = agent.run(input=query)
            print(
                colored("Answer: ", "green", attrs=["bold"]),
                colored(result, "light_green"),
            )
    except (EOFError, KeyboardInterrupt):
        print("\nkthxbye.")
        skynet.turn_off_client()
        exit()


if __name__ == "__main__":
    run()
