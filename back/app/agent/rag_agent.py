"""
RAG Agent
负责从知识库检索相关信息
"""
from typing import Dict, Any, List
from app.rag.rag_service import retrieve_documents
from app.utils.logger import logger


class RAGAgent:
    """RAG Agent 类"""
    
    def __init__(self, top_k: int = 3):
        """
        初始化 RAG Agent
        
        Args:
            top_k: 返回前 k 个最相关的文档
        """
        self.top_k = top_k
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理 RAG 检索
        
        Args:
            state: 当前状态字典，包含 'user_input' 或 'input'
            
        Returns:
            Dict[str, Any]: 更新后的状态，包含 'documents' 键
        """
        try:
            # 获取用户输入
            user_input = state.get("user_input") or state.get("input", "")
            
            if not user_input:
                logger.warning("用户输入为空，无法进行 RAG 检索")
                return {**state, "documents": []}
            
            # 检索相关文档
            documents = retrieve_documents(user_input, top_k=self.top_k)
            
            if not documents:
                logger.warning(f"未检索到相关文档: {user_input[:50]}...")
                return {**state, "documents": []}
            
            logger.info(f"成功检索到 {len(documents)} 个相关文档")
            
            return {
                **state,
                "documents": documents,
                "rag_query": user_input
            }
            
        except Exception as e:
            logger.error(f"RAG Agent 处理失败: {str(e)}")
            return {**state, "documents": [], "error": str(e)}

