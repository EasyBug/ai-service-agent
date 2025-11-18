"""
LangGraph 工作流定义
管理所有 Agent 的流转
"""
from typing import Dict, Any, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from redis import Redis
from app.agent.router_agent import RouterAgent
from app.agent.order_agent import OrderAgent
from app.agent.rag_agent import RAGAgent
from app.agent.llm_agent import LLMAgent
from app.config import settings
from app.utils.logger import logger

try:
    from langgraph.checkpoint.redis import RedisSaver  # type: ignore
    REDIS_CHECKPOINT_AVAILABLE = True
except ImportError:
    # 如果 langgraph.checkpoint.redis 不可用，尝试独立包
    try:
        from langgraph_checkpoint_redis import RedisSaver  # type: ignore
        REDIS_CHECKPOINT_AVAILABLE = True
    except ImportError:
        REDIS_CHECKPOINT_AVAILABLE = False
        logger.warning("Redis checkpoint 不可用，将使用内存 checkpoint")


class AgentState(TypedDict):
    """Agent 状态定义"""
    input: str
    user_input: str
    intent: str
    order: Any
    documents: list
    response: str
    error: str


def create_checkpoint():
    """
    创建 Redis checkpoint 用于状态存储
    
    Returns:
        Checkpoint 实例或 None
    """
    if not REDIS_CHECKPOINT_AVAILABLE:
        logger.warning("Redis checkpoint 模块不可用，将使用内存 checkpoint")
        return None
    
    try:
        # 构建 Redis 连接字符串
        redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
        
        # 测试连接
        test_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )
        test_client.ping()
        test_client.close()
        
        # 创建 RedisSaver
        checkpointer = RedisSaver.from_conn_string(redis_url)
        # 初始化 Redis 索引
        checkpointer.setup()
        
        logger.info("成功创建 Redis checkpoint")
        return checkpointer
        
    except Exception as e:
        logger.warning(f"Redis 连接失败，将使用内存 checkpoint: {str(e)}")
        # 如果 Redis 不可用，返回 None，LangGraph 会使用内存 checkpoint
        return None


def route_after_router(state: AgentState) -> Literal["order", "rag", "llm"]:
    """
    路由函数：根据意图选择下一个节点
    
    Args:
        state: 当前状态
        
    Returns:
        Literal: 下一个节点名称
    """
    intent = state.get("intent", "chat")
    
    if intent == "order":
        return "order"
    elif intent == "rag":
        return "rag"
    else:
        return "llm"


def create_agent_graph(db_session=None):
    """
    创建 Agent 工作流图
    
    Args:
        db_session: 数据库会话（用于 OrderAgent）
        
    Returns:
        StateGraph: LangGraph 状态图
    """
    # 创建各个 Agent 实例
    router_agent = RouterAgent()
    order_agent = OrderAgent(db=db_session)
    rag_agent = RAGAgent()
    llm_agent = LLMAgent()
    
    # 创建状态图
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("router", router_agent.process)
    workflow.add_node("order", order_agent.process)
    workflow.add_node("rag", rag_agent.process)
    workflow.add_node("llm", llm_agent.process)
    
    # 设置入口点
    workflow.set_entry_point("router")
    
    # 添加条件边：根据意图路由
    workflow.add_conditional_edges(
        "router",
        route_after_router,
        {
            "order": "order",
            "rag": "rag",
            "llm": "llm"
        }
    )
    
    # order 和 rag 节点完成后都进入 llm 节点
    workflow.add_edge("order", "llm")
    workflow.add_edge("rag", "llm")
    
    # llm 节点完成后结束
    workflow.add_edge("llm", END)
    
    # 创建 checkpoint（如果可用）
    checkpoint = create_checkpoint()
    
    # 编译图
    if checkpoint:
        app = workflow.compile(checkpointer=checkpoint)
    else:
        app = workflow.compile()
    
    logger.info("成功创建 Agent 工作流图")
    return app


def process_query(
    query: str,
    db_session=None,
    thread_id: str = "default"
) -> Dict[str, Any]:
    """
    处理用户查询（主入口函数）
    
    Args:
        query: 用户查询文本
        db_session: 数据库会话
        thread_id: 线程ID（用于状态管理）
        
    Returns:
        Dict[str, Any]: 处理结果，包含 'response' 键
    """
    try:
        # 创建图
        graph = create_agent_graph(db_session=db_session)
        
        # 初始状态
        initial_state = {
            "input": query,
            "user_input": query,
            "intent": "",
            "order": None,
            "documents": [],
            "response": "",
            "error": ""
        }
        
        # 运行图
        config = {"configurable": {"thread_id": thread_id}}
        result = graph.invoke(initial_state, config=config)
        
        # 返回最终结果
        return {
            "response": result.get("response", "抱歉，无法生成回答。"),
            "intent": result.get("intent", "chat"),
            "order": result.get("order"),
            "documents": result.get("documents", []),
            "error": result.get("error")
        }
        
    except Exception as e:
        logger.error(f"处理查询失败: {str(e)}")
        return {
            "response": "抱歉，处理您的请求时出现错误，请稍后再试。",
            "error": str(e)
        }

