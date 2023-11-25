import langchain
from PIL import Image
from time import sleep
from langchain import hub
from langchain.agents import Tool, AgentType, initialize_agent
from langchain.tools import HumanInputRun, tool
from langchain.chat_models import ChatOpenAI
from langchain.tools.render import render_text_description
from langchain.agents.format_scratchpad import format_log_to_messages
from langchain.agents.output_parsers import JSONAgentOutputParser
from langchain.agents.output_parsers import ReActJsonSingleInputOutputParser
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from termcolor import colored
from fake_client import Client
from human_voice import human_voice_input, human_voice_output
from analyze_image import analyze_image
from agent_prompt import agent_prompt
from langchain.agents import AgentExecutor

llm = ChatOpenAI(temperature=0, model="gpt-4")
robodog = Client()

@tool
def explore(task: str) -> str:
    """You can see what is around you."""
    print("looking around")
    image = robodog.get_image()
    result = analyze_image(image)
    return f"I see: {result}"

@tool
def left(task: str):
    """You can turn left."""
    print("turning left")
    robodog.turn_left()
    sleep(7)
    stop()

@tool
def right(task: str):
    """You can turn right."""
    print("turning right")
    robodog.turn_right()
    sleep(7)
    stop()

@tool
def forward(task: str):
    """You can move forward."""
    print("moving forward")
    robodog.move_forward()
    sleep(7)
    stop()

@tool
def backward(task: str):
    """You can move backward."""
    print("moving backward")
    robodog.move_backward()
    sleep(7)
    stop()

@tool
def obstacle(task: str) -> str:
    """You can check for obstacles in front of you."""
    robodog.get_sonic()
    sleep(1)
    if robodog.sonic < 20:
        return "There is an obstacle in front of me"
    else:
        return "There is no obstacle in front of me"

def stop():
    print("stopping")
    robodog.move_stop()


tools = [
    explore, left, right, forward, backward,obstacle,
    Tool.from_function(
        func=human_voice_input,
        name="ask",
        description="You can ask the human. The input should be a question for the human."
    ),
    Tool.from_function(
        func=human_voice_output,
        name="say",
        description="You can say something to the human."
    ),
]
prompt = hub.pull("hwchase17/react-chat-json")

prompt = prompt.partial(
    tools=render_text_description(tools), 
    tool_names=", ".join([t.name for t in tools])
)
chat_model_with_stop = llm.bind(stop=["\nObservation"])

# We need some extra steering, or the chat model forgets how to respond sometimes
TEMPLATE_TOOL_RESPONSE = """TOOL RESPONSE: 
---------------------
{observation}

USER'S INPUT
--------------------

Okay, so what is the response to my last comment? If using information obtained from the tools you must mention it explicitly without mentioning the tool names - I have forgotten all TOOL RESPONSES! Remember to respond with a markdown code snippet of a json blob with a single action, and NOTHING else - even if you just want to respond to the user. Do NOT respond with anything except a JSON snippet no matter what!"""


agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_log_to_messages(
                x["intermediate_steps"], template_tool_response=TEMPLATE_TOOL_RESPONSE
            ),
            "chat_history": lambda x: x["chat_history"],
        }
        | prompt
        | chat_model_with_stop
        | JSONAgentOutputParser
    )

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    memory=memory,
)


def run():
    print("Connecting to robot")
    robodog.turn_on_client("localhost")
    sleep(2)
    human_voice_output("Hello, i am RoboDog.")
    try:
        while True:
            query = human_voice_input("What should i do now?")
            result = agent_executor.invoke({"input": query})["output"]
            human_voice_output(result)
    except (EOFError, KeyboardInterrupt):
        print("\nkthxbye.")
        robodog.turn_off_client()
        exit()


if __name__ == "__main__":
    print(agent_executor.invoke({"input": "What can you see?"}))
    # run()
