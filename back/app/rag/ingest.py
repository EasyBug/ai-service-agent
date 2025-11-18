"""
知识库文档索引更新脚本
从指定目录加载文档并更新向量索引
"""
import os
import sys
from pathlib import Path
from llama_index.core import SimpleDirectoryReader, Document
from app.rag.rag_service import update_knowledge_base
from app.utils.logger import logger


def ingest_documents(data_dir: str = "data") -> bool:
    """
    从目录加载文档并更新索引
    
    Args:
        data_dir: 文档目录路径
        
    Returns:
        bool: 是否成功
    """
    try:
        # 检查目录是否存在
        data_path = Path(data_dir)
        if not data_path.exists():
            logger.warning(f"文档目录不存在: {data_dir}，将创建空目录")
            data_path.mkdir(parents=True, exist_ok=True)
            logger.info("请将文档放入 data/ 目录后重新运行")
            return False
        
        # 读取文档
        logger.info(f"从 {data_dir} 目录加载文档...")
        reader = SimpleDirectoryReader(input_dir=data_dir, recursive=True)
        documents = reader.load_data()
        
        # 为每个文档添加文件名到 metadata
        for doc in documents:
            if hasattr(doc, 'metadata') and doc.metadata:
                # 如果 metadata 中有 file_path，提取文件名
                file_path = doc.metadata.get('file_path', '')
                if file_path:
                    filename = Path(file_path).name
                    doc.metadata['filename'] = filename
                    doc.metadata['file_path'] = str(file_path)
        
        if not documents:
            logger.warning("未找到任何文档")
            return False
        
        logger.info(f"成功加载 {len(documents)} 个文档")
        
        # 更新知识库
        success = update_knowledge_base(documents)
        
        if success:
            logger.info("知识库更新成功")
        else:
            logger.error("知识库更新失败")
        
        return success
        
    except Exception as e:
        logger.error(f"文档索引更新失败: {str(e)}")
        return False


if __name__ == "__main__":
    # 从命令行参数获取目录，默认为 data
    data_directory = sys.argv[1] if len(sys.argv) > 1 else "data"
    
    logger.info("开始更新知识库索引...")
    success = ingest_documents(data_directory)
    
    if success:
        logger.info("知识库索引更新完成")
        sys.exit(0)
    else:
        logger.error("知识库索引更新失败")
        sys.exit(1)

