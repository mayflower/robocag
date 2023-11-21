import langchain
from PIL import Image
from time import sleep
from langchain.agents import Tool, AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools.render import render_text_description
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryBufferMemory
from termcolor import colored
from RobodogClient.client import Client
from agent_prompt import agent_prompt
from langchain.agents import AgentExecutor
from human_voice_input import human_voice_input
from analyze_image import analyze_image
from langchain.agents import load_tools

MODEL = "gpt-4"

langchain.debug = True
llm = ChatOpenAI(temperature=0, model=MODEL)
skynet = Client()
skynet.turn_on_client("10.93.16.138")
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
    image = skynet.get_image()
    result = analyze_image(image)
    # image = transform(skynet.get_image()).unsqueeze(0).to(device)
    # res = inference(image, model)
    # print("I see: " + res[0] + " in front of me")
    return f"I see: {result}"


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

human_tool = load_tools(["human"])[0]

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
    # Tool.from_function(
    #     func=human_voice_input,
    #     name="Human",
    #     description=(
    #         "You can ask a human for guidance when you think you "
    #         "got stuck or you are not sure what to do next. "
    #         "The input should be a question for the human."
    #     )
    # )
    human_tool
]

systemprompt = """You are a dog that can look, listen, move and speak. 
Your Owner is a human that can give you commands.


"""

prompt = agent_prompt.partial(tools=render_text_description(tools), tool_names=", ".join([t.name for t in tools]))
llm_with_stop = llm.bind(stop=["\nObservation"])

agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_log_to_str(
                x["intermediate_steps"]
            ),
            "chat_history": lambda x: x["chat_history"],
        }
        | prompt
        | llm_with_stop
        | ReActSingleInputOutputParser()
    )

memory = ConversationSummaryBufferMemory(
        llm=llm, memory_key="chat_history", return_messages=True
    )
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    memory=memory,
)

def run():
    skynet.turn_on_client("skynet")
    sleep(3)
    print(colored("Hello, i am RoboDog. What can i do for you?", "green"))
    try:
        while True:
            # query = human_voice_input("Hi, ich bin die Mayflower MesseKatze, was kann ich für dich tun?")

            query = input(colored("You: ", "white", attrs=["bold"]))
            print(query)
            print(agent_executor.InputType)
            result = agent_executor.invoke({"input": query})["output"]
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