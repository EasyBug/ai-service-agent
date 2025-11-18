"""
索引加载模块
从 PostgreSQL + pgvector 加载 LlamaIndex 索引
"""
from typing import Optional
from llama_index.core import VectorStoreIndex, Settings
from sqlalchemy import create_engine
from app.config import settings
from app.clients.llm_client import llm_client
from app.utils.logger import logger

# 尝试不同的导入路径
try:
    from llama_index.vector_stores.postgres import PGVectorStore  # type: ignore
except ImportError:
    try:
        from llama_index_vector_stores_postgres import PGVectorStore  # type: ignore
    except ImportError:
        # 如果都失败，尝试从 core 导入
        try:
            from llama_index.core.vector_stores.postgres import PGVectorStore  # type: ignore
        except ImportError:
            PGVectorStore = None
            logger.warning("PGVectorStore 不可用，请安装 llama-index-vector-stores-postgres")

# 尝试导入 Gemini Embedding
try:
    from llama_index.embeddings.gemini import GeminiEmbedding  # type: ignore
except ImportError:
    try:
        from llama_index_embeddings_gemini import GeminiEmbedding  # type: ignore
    except ImportError:
        GeminiEmbedding = None
        logger.warning("GeminiEmbedding 不可用，请安装 llama-index-embeddings-gemini")


def load_index(
    table_name: str = "llama_index_vectors",  # PGVectorStore 会自动添加 data_ 前缀
    embed_dim: int = 3072  # GeminiEmbedding 实际维度
) -> Optional[VectorStoreIndex]:
    """
    从 PostgreSQL 加载向量索引
    
    Args:
        table_name: 向量表名
        embed_dim: 嵌入向量维度（GeminiEmbedding 实际为 3072）
        
    Returns:
        Optional[VectorStoreIndex]: 向量索引对象，如果加载失败返回 None
    """
    try:
        # 检查必要的模块是否可用
        if PGVectorStore is None:
            logger.error("PGVectorStore 未安装，请运行: pip install llama-index-vector-stores-postgres")
            return None
        
        if GeminiEmbedding is None:
            logger.error("GeminiEmbedding 未安装，请运行: pip install llama-index-embeddings-gemini")
            return None
        
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
        
        # 设置全局嵌入模型
        Settings.embed_model = embed_model
        
        # 创建 PGVectorStore
        vector_store = PGVectorStore.from_params(
            database=settings.POSTGRES_DB,
            host=settings.POSTGRES_HOST,
            password=settings.POSTGRES_PASSWORD,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            table_name=table_name,
            embed_dim=embed_dim
        )
        
        # 从向量存储加载索引
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=embed_model
        )
        
        logger.info("成功加载向量索引")
        return index
        
    except Exception as e:
        logger.error(f"加载向量索引失败: {str(e)}")
        return None


def get_or_create_index(
    table_name: str = "llama_index_vectors",  # PGVectorStore 会自动添加 data_ 前缀
    embed_dim: int = 3072  # GeminiEmbedding 实际维度
) -> Optional[VectorStoreIndex]:
    """
    获取或创建索引（如果不存在则创建）
    
    Args:
        table_name: 向量表名
        embed_dim: 嵌入向量维度
        
    Returns:
        Optional[VectorStoreIndex]: 向量索引对象
    """
    index = load_index(table_name, embed_dim)
    
    # 如果索引不存在，创建一个新的
    if index is None:
        try:
            # 检查必要的模块是否可用
            if PGVectorStore is None or GeminiEmbedding is None:
                logger.error("必要的模块未安装")
                return None
            
            connection_string = (
                f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
                f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
            )
            
            engine = create_engine(connection_string)
            
            embed_model = GeminiEmbedding(
                model_name="models/gemini-embedding-001",
                api_key=settings.GEMINI_API_KEY
            )
            
            Settings.embed_model = embed_model
            
            vector_store = PGVectorStore.from_params(
                database=settings.POSTGRES_DB,
                host=settings.POSTGRES_HOST,
                password=settings.POSTGRES_PASSWORD,
                port=settings.POSTGRES_PORT,
                user=settings.POSTGRES_USER,
                table_name=table_name,
                embed_dim=embed_dim
            )
            
            index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                embed_model=embed_model
            )
            
            logger.info("创建新的向量索引")
            return index
            
        except Exception as e:
            logger.error(f"创建向量索引失败: {str(e)}")
            return None
    
    return index

