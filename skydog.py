import langchain
from PIL import Image
from time import sleep
from langchain.agents import Tool, AgentType, initialize_agent
from langchain.tools import HumanInputRun, tool
from langchain.chat_models import ChatOpenAI
from langchain.tools.render import render_text_description
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryBufferMemory
from termcolor import colored
from fake_client import Client
from human_voice import human_voice_input, human_voice_output
from analyze_image import analyze_image
from agent_prompt import agent_prompt
from langchain.agents import AgentExecutor

MODEL = "gpt-4"

llm = ChatOpenAI(temperature=0, model=MODEL)
skynet = Client()

def look_around(task: str):
    """observe the environment"""
    print("looking around")
    image = skynet.get_image()
    result = analyze_image(image)
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
    Tool.from_function(
        func=human_voice_input,
        name="ask",
        description=(
            "You can ask a human for guidance when you think you "
            "got stuck or you are not sure what to do next. "
            "The input should be a question for the human."
        )
    ),
    Tool.from_function(
        func=human_voice_output,
        name="say",
        description="say something to the user when you don't expect an answer."
    ),
]

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
    print("Connecting to robot")
    skynet.turn_on_client("localhost")
    sleep(3)
    human_voice_output("Hello, i am RoboDog. What can i do for you?")
    try:
        while True:
            query = human_voice_input("What should i do now?")
            result = agent_executor.invoke({"input": query})["output"]
            human_voice_output(result)
    except (EOFError, KeyboardInterrupt):
        print("\nkthxbye.")
        skynet.turn_off_client()
        exit()


if __name__ == "__main__":
    run()
