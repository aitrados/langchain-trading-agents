from loguru import logger
from langchain_trading_agents.bus_controls.bus_control_mixin import BusControlMixin
import asyncio
import json
from typing import List, TypedDict, Annotated, Dict


from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

from pydantic import BaseModel, Field

from langchain_trading_agents.llm_model.sub_agents import BaseSubAgent,  ManagerAnalyst, DecisionMakerAnalyst

from langgraph.graph import StateGraph, END

from langchain_trading_agents.utils.common_utils import get_or_create_conversation_id


class AgentTask(BaseModel):
    department: str = Field(description="The name of the department to which this task should be assigned.")
    task_prompt: str = Field(description="A specific and executable instruction prompt generated for the agent of this department.")

class GraphState(TypedDict, total=False):
    original_query: str  # The user's original query.

    # Output of the Planner node
    plan: List[AgentTask]

    # Output of the Sub-agent nodes
    sub_agent_results: Annotated[List[Dict[str, str]], lambda x, y: x + y]

    # Output of the Summarizer node
    decision_maker_summary: str



class AiBusControl(BusControlMixin):
    """
    Orchestrates a multi-agent system for analyzing user queries.

    This class manages a workflow where a manager agent breaks down a query into tasks,
    sub-agents execute these tasks in parallel, and a decision-maker agent synthesizes
    the results into a final response.
    """
    def __init__(self, manager_analyst:ManagerAnalyst, decision_maker_analyst:DecisionMakerAnalyst,team="AITRADOS AI team",slogan="Making stable money every day is our ultimate goal"):
        """
        Initializes the AiBusControl.

        This sets up the core components of the agent orchestration system,
        including the manager and decision-maker analysts, and prepares the
        execution workflow.

        Args:
            manager_analyst: An instance of ManagerAnalyst, responsible for planning.
            decision_maker_analyst: An instance of DecisionMakerAnalyst, responsible for summarizing.
        """
        self.manager_analyst=manager_analyst
        self.decision_maker_analyst=decision_maker_analyst
        self.team=team
        self.slogan=slogan

        self.decision_maker_analyst._bus_control=self
        self.manager_analyst._bus_control = self


        self.sub_agent_registry: Dict[str, BaseSubAgent] = {}

        # Build and compile the graph at initialization, only once.
        self._build_workflow()
        self.conversation_id:str=None
        super().__init__()

    def _build_workflow(self):
        """Builds the workflow graph. This is called only once during initialization."""
        workflow = StateGraph(GraphState)
        # Add nodes
        workflow.add_node("manager", self._manager_node)
        workflow.add_node("sub_agents", self._sub_agent_node)
        workflow.add_node("decision_maker", self._decision_maker_node)

        # Set up the flow
        workflow.set_entry_point("manager")
        workflow.add_edge("manager", "sub_agents")
        workflow.add_edge("sub_agents", "decision_maker")
        workflow.add_edge("decision_maker", END)

        # Compile the graph and save it as an instance attribute
        self.app = workflow.compile()

    def add_sub_agent(self, *sub_agents: BaseSubAgent):
        """
        Registers one or more sub-agents.

        Each sub-agent is mapped to a specific department, allowing the bus control
        to delegate tasks accordingly.

        Args:
            *sub_agents: A variable number of BaseSubAgent instances to be added.
        """
        for sub_agent in sub_agents:
            sub_agent._bus_control=self
            sub_agent.init_data()
            self.sub_agent_registry[sub_agent.department] = sub_agent

    async def a_analyze(self, user_query: str,conversation_id: str = None):
        """
        Asynchronously analyzes a user query by running it through the compiled workflow.

        This is the main entry point for processing a user request. It triggers the
        manager, sub-agents, and decision-maker nodes in sequence.

        Args:
            user_query: The user's query to be analyzed.
            conversation_id: An optional ID to track the conversation history.

        Returns:
            The final result from the decision-maker node.
        """
        self.conversation_id = get_or_create_conversation_id(conversation_id)

        if not self.sub_agent_registry:
            raise ValueError("At least one sub-agent must be added. Use the self.add_sub_agent method to add an analysis department.")
        if not user_query:
            raise ValueError("user_query cannot be empty. Please provide the user's query content.")
        return await self.app.ainvoke({
            "original_query": user_query
        })
    # Convert the original global function into an instance method
    async def _manager_node(self, state: GraphState) -> dict:
        """Planner node: Receives the user's query and breaks it down into sub-tasks."""
        logger.info(f"TEAM: {self.team}")
        logger.info(f"SLOGAN: {self.slogan}")
        logger.info(f"User query: {state['original_query']}")


        logger.info("🫡 Fund manager is thinking...")
        if self.manager_analyst.custom_mcp_department:
            response_str=await self.manager_analyst.analyze(state['original_query'],conversation_id=self.conversation_id)
        else:
            response_str = await self.manager_analyst.analyze_without_tools(state['original_query'],
                                                                            conversation_id=self.conversation_id)
        try:
            plan_list=await JsonOutputParser().ainvoke(response_str)
            plan_tasks = [AgentTask(**item) for item in plan_list]
            logger.info(f"✅ Fund manager planning complete. Number of tasks: {len(plan_tasks)}")
            return {"plan": plan_tasks}
        except json.JSONDecodeError as e:
            logger.error(f"❌ Fund manager planning failed. JSON parsing error: {e}. You may need to optimize your query or system prompt.")
            logger.error(f"Fund manager original response: {response_str}")
            return {"plan": []}

    async def _sub_agent_node(self, state: GraphState) -> dict:
        """Sub-agent execution node: Processes all planned tasks in parallel."""
        plan = state["plan"]
        if not plan:
            return {"sub_agent_results": []}

        async def run_agent_task(task: AgentTask):
            department = task.department
            prompt = task.task_prompt
            agent = self.sub_agent_registry.get(department)

            if not agent:
                logger.error(f"⚠️ Agent for department '{department}' not found. Please check if the department was added using self.add_sub_agent.")
                return {"department": department, "result": f"Error: Corresponding agent for department '{department}' not found."}

            logger.info(f"🚀 Calling {agent.nickname} (Department: {department})")
            logger.info(f"   Task prompt: {prompt}")

            try:
                result_content = await agent.analyze(prompt,conversation_id=self.conversation_id)
                if agent.output_parse:
                    result_content=await agent.output_parse.ainvoke(result_content)
                    if isinstance(result_content,dict|list):
                        result_content=json.dumps(result_content)
                    elif not isinstance(result_content,str):
                        result_content=str(result_content)

                logger.success(f"✅ {department}: {agent.nickname} analysis complete.")
                return {"department": department, "result": result_content}
            except Exception as e:
                logger.error(f"❌ {agent.nickname} analysis failed: {e}. You may need to optimize your query or system prompt.")
                return {"department": department, "result": f"An error occurred during analysis: {str(e)}"}

        # Execute all tasks in parallel
        tasks = [run_agent_task(task) for task in plan]
        results = await asyncio.gather(*tasks)
        logger.success("✅ All sub-agent analyses are complete.")
        return {"sub_agent_results": results}

    async def _decision_maker_node(self, state: GraphState) -> dict:
        """Summarizer node: Consolidates all sub-agent responses to generate a final report."""
        sub_agent_results = state['sub_agent_results']

        if not sub_agent_results:
            return {"decision_maker_summary": "Failed to generate any analysis results from sub agents."}

        manager_collected_reports = "\n\n".join(
            [f"From [{item['department']}] department analysis:\n{item['result']}\n\n" for item in sub_agent_results]
        )

        self.decision_maker_analyst.placeholder_map["manager_collected_reports"]=manager_collected_reports

        logger.info("🤬 Decision maker is making a decision...")
        if self.decision_maker_analyst.custom_mcp_department:
            decision_maker_summary = await self.decision_maker_analyst.analyze(state['original_query'],conversation_id=self.conversation_id)
        else:
            decision_maker_summary=await self.decision_maker_analyst.analyze_without_tools(state['original_query'],conversation_id=self.conversation_id)

        logger.success("✅ Final report generated successfully.")
        return {"decision_maker_summary": decision_maker_summary}