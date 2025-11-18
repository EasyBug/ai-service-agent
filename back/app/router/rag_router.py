"""
RAG 知识库更新路由
"""
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from typing import List, Optional
from app.rag.rag_service import update_knowledge_base
from app.rag.ingest import ingest_documents
from app.utils.response import create_response
from app.utils.logger import logger

router = APIRouter()

# 数据目录路径
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


@router.post("/update")
async def update_rag():
    """
    更新知识库索引
    
    从 data/ 目录加载文档并更新向量索引
    
    Returns:
        dict: 更新结果
    """
    try:
        logger.info("开始更新知识库索引...")
        
        # 从 data/ 目录加载文档并更新索引
        success = ingest_documents("data")
        
        if success:
            return create_response(
                data={"status": "success"},
                message="知识库更新成功",
                success=True
            )
        else:
            return create_response(
                data={"status": "failed"},
                message="知识库更新失败，请检查日志",
                success=False,
                status_code=500,
                error="更新失败"
            )
        
    except Exception as e:
        logger.error(f"知识库更新失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"知识库更新失败: {str(e)}"
        )


@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    上传文件到知识库
    
    支持的文件格式：txt, md, pdf
    
    Args:
        files: 上传的文件列表
        
    Returns:
        dict: 上传结果
    """
    try:
        if not files:
            return create_response(
                data=None,
                message="请选择要上传的文件",
                success=False,
                status_code=400,
                error="未选择文件"
            )
        
        # 支持的文件扩展名
        allowed_extensions = {".txt", ".md", ".pdf"}
        
        uploaded_files = []
        failed_files = []
        
        for file in files:
            try:
                # 检查文件扩展名
                file_ext = Path(file.filename).suffix.lower()
                if file_ext not in allowed_extensions:
                    failed_files.append({
                        "filename": file.filename,
                        "reason": f"不支持的文件格式: {file_ext}"
                    })
                    continue
                
                # 保存文件到 data 目录
                file_path = DATA_DIR / file.filename
                
                # 如果文件已存在，添加序号
                counter = 1
                original_path = file_path
                while file_path.exists():
                    stem = original_path.stem
                    suffix = original_path.suffix
                    file_path = DATA_DIR / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                # 读取并保存文件内容
                content = await file.read()
                with open(file_path, "wb") as f:
                    f.write(content)
                
                uploaded_files.append({
                    "filename": file_path.name,
                    "size": len(content)
                })
                
                logger.info(f"成功上传文件: {file_path.name} ({len(content)} bytes)")
                
            except Exception as e:
                logger.error(f"上传文件 {file.filename} 失败: {str(e)}")
                failed_files.append({
                    "filename": file.filename,
                    "reason": str(e)
                })
        
        if not uploaded_files:
            return create_response(
                data={
                    "uploaded": uploaded_files,
                    "failed": failed_files
                },
                message="所有文件上传失败",
                success=False,
                status_code=400,
                error="上传失败"
            )
        
        return create_response(
            data={
                "uploaded": uploaded_files,
                "failed": failed_files
            },
            message=f"成功上传 {len(uploaded_files)} 个文件",
            success=True
        )
        
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"文件上传失败: {str(e)}"
        )


@router.post("/upload-and-update")
async def upload_and_update(files: List[UploadFile] = File(...)):
    """
    上传文件并立即更新知识库
    
    支持的文件格式：txt, md, pdf
    
    Args:
        files: 上传的文件列表
        
    Returns:
        dict: 上传和更新结果
    """
    try:
        if not files:
            return create_response(
                data=None,
                message="请选择要上传的文件",
                success=False,
                status_code=400,
                error="未选择文件"
            )
        
        # 支持的文件扩展名
        allowed_extensions = {".txt", ".md", ".pdf"}
        
        uploaded_files = []
        failed_files = []
        
        for file in files:
            try:
                # 检查文件扩展名
                file_ext = Path(file.filename).suffix.lower()
                if file_ext not in allowed_extensions:
                    failed_files.append({
                        "filename": file.filename,
                        "reason": f"不支持的文件格式: {file_ext}"
                    })
                    continue
                
                # 保存文件到 data 目录
                file_path = DATA_DIR / file.filename
                
                # 如果文件已存在，添加序号
                counter = 1
                original_path = file_path
                while file_path.exists():
                    stem = original_path.stem
                    suffix = original_path.suffix
                    file_path = DATA_DIR / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                # 读取并保存文件内容
                content = await file.read()
                with open(file_path, "wb") as f:
                    f.write(content)
                
                uploaded_files.append({
                    "filename": file_path.name,
                    "size": len(content)
                })
                
                logger.info(f"成功上传文件: {file_path.name} ({len(content)} bytes)")
                
            except Exception as e:
                logger.error(f"上传文件 {file.filename} 失败: {str(e)}")
                failed_files.append({
                    "filename": file.filename,
                    "reason": str(e)
                })
        
        if not uploaded_files:
            return create_response(
                data={
                    "uploaded": uploaded_files,
                    "failed": failed_files
                },
                message="所有文件上传失败",
                success=False,
                status_code=400,
                error="上传失败"
            )
        
        # 然后更新知识库
        logger.info("开始更新知识库索引...")
        success = ingest_documents(str(DATA_DIR))
        
        if success:
            return create_response(
                data={
                    "uploaded": uploaded_files,
                    "failed": failed_files,
                    "index_updated": True
                },
                message="文件上传成功，知识库已更新",
                success=True
            )
        else:
            return create_response(
                data={
                    "uploaded": uploaded_files,
                    "failed": failed_files,
                    "index_updated": False
                },
                message="文件上传成功，但知识库更新失败",
                success=False,
                status_code=500,
                error="知识库更新失败"
            )
        
    except Exception as e:
        logger.error(f"上传并更新失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"上传并更新失败: {str(e)}"
        )


@router.get("/files")
async def list_rag_files():
    """
    获取知识库文件列表
    
    返回 data/ 目录中的文件列表
    
    Returns:
        dict: 文件列表
    """
    try:
        import os
        from pathlib import Path
        
        # 获取 data 目录中的所有文件
        files = []
        if DATA_DIR.exists():
            for file_path in DATA_DIR.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in {".txt", ".md", ".pdf"}:
                    file_stat = file_path.stat()
                    files.append({
                        "filename": file_path.name,
                        "size": file_stat.st_size,
                        "modified": file_path.stat().st_mtime
                    })
        
        # 按文件名排序
        files.sort(key=lambda x: x["filename"])
        
        return create_response(
            data={"files": files},
            message=f"找到 {len(files)} 个文件",
            success=True
        )
        
    except Exception as e:
        logger.error(f"获取文件列表失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取文件列表失败: {str(e)}"
        )


@router.delete("/clear")
async def clear_rag(filename: Optional[str] = Query(None, description="要删除的文件名（可选）")):
    """
    删除知识库内容
    
    如果提供 filename，则删除指定文件的内容
    如果不提供 filename，则清空整个知识库
    
    Args:
        filename: 要删除的文件名（可选）
        
    Returns:
        dict: 删除结果
    """
    try:
        from sqlalchemy import create_engine, text
        from app.config import settings
        import json
        
        # 构建 PostgreSQL 连接 URL
        connection_string = (
            f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )
        
        # 创建数据库引擎
        engine = create_engine(connection_string)
        
        # 向量表名（PGVectorStore 会自动添加 data_ 前缀）
        table_name = "data_llama_index_vectors"
        
        with engine.connect() as conn:
            # 检查表是否存在
            check_table = text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = '{table_name}'
                );
            """)
            result = conn.execute(check_table)
            table_exists = result.scalar()
            
            if not table_exists:
                logger.warning(f"向量表 {table_name} 不存在")
                return create_response(
                    data={"deleted_count": 0},
                    message="知识库为空",
                    success=True
                )
            
            if filename:
                # 删除指定文件的内容
                # 通过 metadata 中的 file_path 或 source 字段匹配文件名
                logger.info(f"开始删除文件: {filename}")
                
                # 使用 JSON 操作符精确匹配
                # 1. 匹配 metadata->>'file_path' 以文件名结尾
                # 2. 匹配 metadata->>'source' 等于文件名
                # 3. 匹配 metadata->>'filename' 等于文件名
                
                delete_query = text(f"""
                    DELETE FROM {table_name}
                    WHERE (metadata_->>'file_path' IS NOT NULL 
                           AND (metadata_->>'file_path' LIKE :pattern1 
                                OR metadata_->>'file_path' LIKE :pattern2
                                OR metadata_->>'file_path' = :filename))
                       OR (metadata_->>'source' IS NOT NULL 
                           AND metadata_->>'source' = :filename)
                       OR (metadata_->>'filename' IS NOT NULL 
                           AND metadata_->>'filename' = :filename);
                """)
                
                # 构建匹配模式
                # 1. 文件路径以 /filename 结尾（Unix/Mac 路径）
                # 2. 文件路径以 \\filename 结尾（Windows 路径）
                pattern1 = f'%/{filename}'
                pattern2 = f'%\\{filename}'
                
                result = conn.execute(
                    delete_query,
                    {"pattern1": pattern1, "pattern2": pattern2, "filename": filename}
                )
                deleted_count = result.rowcount
                conn.commit()
                
                # 同时删除文件（如果存在）
                file_path = DATA_DIR / filename
                file_deleted = False
                if file_path.exists():
                    try:
                        file_path.unlink()
                        file_deleted = True
                        logger.info(f"已删除文件: {filename}")
                    except Exception as e:
                        logger.warning(f"删除文件失败: {str(e)}")
                
                logger.info(f"成功删除文件 {filename}，删除了 {deleted_count} 条记录")
                
                return create_response(
                    data={
                        "deleted_count": deleted_count,
                        "filename": filename,
                        "file_deleted": file_deleted
                    },
                    message=f"成功删除文件 {filename}，删除了 {deleted_count} 条记录",
                    success=True
                )
            else:
                # 清空整个知识库
                logger.info("开始清空知识库索引...")
                
                delete_query = text(f"DELETE FROM {table_name};")
                result = conn.execute(delete_query)
                deleted_count = result.rowcount
                conn.commit()
                
                logger.info(f"成功清空知识库，删除了 {deleted_count} 条记录")
                
                return create_response(
                    data={"deleted_count": deleted_count},
                    message=f"成功清空知识库，删除了 {deleted_count} 条记录",
                    success=True
                )
        
    except Exception as e:
        logger.error(f"删除知识库失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"删除知识库失败: {str(e)}"
        )

