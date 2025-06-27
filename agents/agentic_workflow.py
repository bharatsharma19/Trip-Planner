from langgraph.graph import StateGraph, MessagesState, END, START
from langgraph.prebuilt import ToolNode, tools_condition

from utils.model_loader import ModelLoader
from prompt_library.prompt import SYSTEM_PROMPT

from tools.weather_info_tool import weather_info
from tools.search_place_tool import search_place
from tools.calculator_tool import calculator
from tools.currency_conversion_tool import currency_converter


class GraphBuilder:
    def __init__(self, model_provider="google"):
        # Load tools and system prompt once
        self.tools = [
            weather_info,
            search_place,
            calculator,
            currency_converter,
        ]
        self.system_prompt = SYSTEM_PROMPT
        self.llm_with_tools = ModelLoader(model_provider=model_provider).load_llm()

        # Compile graph once at initialization
        self.graph = self._build_graph()

    def _agent_node(self, state: MessagesState):
        """
        Node function to handle agent interaction.
        """
        user_messages = state["messages"]
        full_prompt = [self.system_prompt] + user_messages
        response = self.llm_with_tools.invoke(full_prompt)
        return {"messages": [response]}

    def _build_graph(self):
        """
        Constructs and compiles the LangGraph workflow once.
        """
        graph_builder = StateGraph(MessagesState)

        # Define graph nodes
        graph_builder.add_node("agent", self._agent_node)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))

        # Define graph edges
        graph_builder.add_edge(START, "agent")
        graph_builder.add_conditional_edges("agent", tools_condition)
        graph_builder.add_edge("tools", "agent")
        graph_builder.add_edge("agent", END)

        return graph_builder.compile()

    def __call__(self):
        """
        Returns the compiled LangGraph instance.
        """
        return self.graph
