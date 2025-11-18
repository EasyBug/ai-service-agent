"""
RAG 服务模块
提供知识库检索功能
"""
from typing import List, Dict, Any, Optional
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.core.node_parser import SimpleNodeParser
from sqlalchemy import create_engine
from app.config import settings
from app.rag.index_loader import get_or_create_index
from app.utils.logger import logger

# 尝试不同的导入路径
try:
    from llama_index.vector_stores.postgres import PGVectorStore  # type: ignore
except ImportError:
    try:
        from llama_index_vector_stores_postgres import PGVectorStore  # type: ignore
    except ImportError:
        try:
            from llama_index.core.vector_stores.postgres import PGVectorStore  # type: ignore
        except ImportError:
            PGVectorStore = None
            logger.warning("PGVectorStore 不可用，请安装 llama-index-vector-stores-postgres")

try:
    from llama_index.embeddings.gemini import GeminiEmbedding  # type: ignore
except ImportError:
    try:
        from llama_index_embeddings_gemini import GeminiEmbedding  # type: ignore
    except ImportError:
        GeminiEmbedding = None
        logger.warning("GeminiEmbedding 不可用，请安装 llama-index-embeddings-gemini")


class RAGService:
    """RAG 服务类"""
    
    def __init__(self):
        """初始化 RAG 服务"""
        self.index: Optional[VectorStoreIndex] = None
        self.table_name = "llama_index_vectors"  # PGVectorStore 会自动添加 data_ 前缀
        self.embed_dim = 3072  # GeminiEmbedding 实际维度（不是 768）
    
    def _ensure_index(self) -> bool:
        """
        确保索引已加载
        
        Returns:
            bool: 是否成功加载索引
        """
        if self.index is None:
            self.index = get_or_create_index(self.table_name, self.embed_dim)
        return self.index is not None
    
    def retrieve_documents(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            top_k: 返回前 k 个最相关的文档
            
        Returns:
            List[Dict[str, Any]]: 检索到的文档列表
        """
        try:
            if not self._ensure_index():
                logger.warning("索引未加载，无法检索文档")
                return []
            
            # 创建检索器
            retriever = self.index.as_retriever(similarity_top_k=top_k)
            
            # 检索相关节点
            nodes = retriever.retrieve(query)
            
            # 转换为字典格式
            results = []
            for node in nodes:
                results.append({
                    "text": node.text,
                    "score": node.score if hasattr(node, 'score') else None,
                    "metadata": node.metadata if hasattr(node, 'metadata') else {}
                })
            
            logger.info(f"检索到 {len(results)} 个相关文档")
            return results
            
        except Exception as e:
            logger.error(f"检索文档失败: {str(e)}")
            return []
    
    def update_knowledge_base(
        self,
        documents: List[Document],
        table_name: Optional[str] = None
    ) -> bool:
        """
        更新知识库索引
        
        Args:
            documents: 文档列表
            table_name: 向量表名，如果不提供则使用默认值
            
        Returns:
            bool: 是否更新成功
        """
        try:
            # 检查必要的模块是否可用
            if PGVectorStore is None:
                logger.error("PGVectorStore 未安装，请运行: pip install llama-index-vector-stores-postgres")
                return False
            
            if GeminiEmbedding is None:
                logger.error("GeminiEmbedding 未安装，请运行: pip install llama-index-embeddings-gemini")
                return False
            
            table_name = table_name or self.table_name
            
            # 构建 PostgreSQL 连接 URL
            connection_string = (
                f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
                f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
            )
            
            # 创建数据库引擎
            engine = create_engine(connection_string)
            
            # 配置 Gemini Embedding
            embed_model = GeminiEmbedding(
                model_name="models/gemini-embedding-001",
                api_key=settings.GEMINI_API_KEY
            )
            
            Settings.embed_model = embed_model
            
            # 创建 PGVectorStore
            vector_store = PGVectorStore.from_params(
                database=settings.POSTGRES_DB,
                host=settings.POSTGRES_HOST,
                password=settings.POSTGRES_PASSWORD,
                port=settings.POSTGRES_PORT,
                user=settings.POSTGRES_USER,
                table_name=table_name,
                embed_dim=self.embed_dim
            )
            
            # 创建节点解析器
            node_parser = SimpleNodeParser.from_defaults(
                chunk_size=512,
                chunk_overlap=50
            )
            
            # 解析文档为节点
            logger.info("解析文档为节点...")
            nodes = node_parser.get_nodes_from_documents(documents, show_progress=True)
            logger.info(f"生成了 {len(nodes)} 个节点")
            
            # 为节点生成嵌入向量
            logger.info("生成嵌入向量...")
            for node in nodes:
                if not hasattr(node, 'embedding') or node.embedding is None:
                    node.embedding = embed_model.get_text_embedding(node.text)
            
            # 直接添加到向量存储
            logger.info("添加节点到向量存储...")
            vector_store.add(nodes)
            
            # 创建索引（用于检索）
            index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                embed_model=embed_model
            )
            
            # 更新实例索引
            self.index = index
            
            logger.info(f"成功更新知识库，共 {len(documents)} 个文档，{len(nodes)} 个节点")
            return True
            
        except Exception as e:
            logger.error(f"更新知识库失败: {str(e)}")
            return False


# 创建全局 RAG 服务实例
rag_service = RAGService()


def retrieve_documents(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    检索相关文档（便捷函数）
    
    Args:
        query: 查询文本
        top_k: 返回前 k 个最相关的文档
        
    Returns:
        List[Dict[str, Any]]: 检索到的文档列表
    """
    return rag_service.retrieve_documents(query, top_k)


def update_knowledge_base(documents: List[Document]) -> bool:
    """
    更新知识库（便捷函数）
    
    Args:
        documents: 文档列表
        
    Returns:
        bool: 是否更新成功
    """
    return rag_service.update_knowledge_base(documents)

