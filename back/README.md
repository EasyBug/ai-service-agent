# Smart Support Agent Backend

智能客服系统后端项目，基于 FastAPI、LangGraph、LlamaIndex、PostgreSQL、Redis 和 n8n 构建。

## 技术栈

- **FastAPI**: Web 框架，提供 RESTful API
- **LangGraph**: Agent 工作流编排
- **LlamaIndex**: RAG 知识库检索
- **PostgreSQL + pgvector**: 数据存储和向量存储
- **Redis**: LangGraph 状态存储和缓存
- **n8n**: 自动化工作流（邮件发送）
- **Google Gemini**: LLM 和 Embedding 模型

## 项目结构

```
smart-support-agent-backend/
├── app/
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理
│   ├── deps.py                 # 依赖注入
│   ├── router/                 # API 路由
│   ├── agent/                  # LangGraph Agents
│   ├── rag/                    # RAG 服务
│   ├── db/                     # 数据库模型和操作
│   ├── clients/                # 外部服务客户端
│   └── utils/                  # 工具类
├── tests/                      # 测试文件
├── .env.example                # 环境变量模板
├── requirements.txt            # Python 依赖
└── README.md                   # 项目说明
```

## 快速开始

### 1. 环境配置

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入：
- PostgreSQL 连接信息
- Redis 连接信息
- Gemini API Key
- n8n Webhook URL（可选，用于订单邮件通知）

**注意**：n8n Webhook URL 是可选的。如果未配置，系统会记录警告但不会影响订单查询功能。详细配置说明请参考 [N8N_SETUP_GUIDE.md](./N8N_SETUP_GUIDE.md)。

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 数据库初始化

#### 安装 PostgreSQL 和 pgvector 扩展

```bash
# 创建数据库
createdb ai_db

# 连接到数据库并启用 pgvector 扩展
psql ai_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

#### 创建数据表

运行初始化脚本：

```bash
python init_db.py
```

或使用 Python 代码：

```python
from app.db.base import Base
from app.db.session import engine

# 创建所有表
Base.metadata.create_all(bind=engine)
```

### 4. 启动 Redis

```bash
# 使用 Docker
docker run -d -p 6379:6379 redis:latest

# 或使用本地 Redis
redis-server
```

### 5. 初始化知识库（可选）

将知识库文档放入 `data/` 目录，然后运行：

```bash
python app/rag/ingest.py
```

### 6. 启动 FastAPI 服务

```bash
# 开发模式（自动重载）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

服务启动后，访问：
- API 文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## API 端点

### 1. 主查询接口

```bash
POST /query
Content-Type: application/json

{
  "query": "用户查询内容"
}
```

该接口会通过 LangGraph 工作流处理查询：
- RouterAgent 判断意图
- 根据意图路由到相应 Agent
- 最终返回 LLM 生成的回答

### 2. 订单查询接口

```bash
GET /order/query?order_id=ORDER123
```

查询订单信息，并自动触发 n8n webhook 发送邮件通知。

### 3. 知识库更新接口

```bash
POST /rag/update
```

更新 LlamaIndex 知识库索引。

### 4. 健康检查

```bash
GET /health
```

## LangGraph 工作流

```
User Input
   ↓
RouterAgent → 意图分类
   ├── order → OrderAgent → n8n 邮件 → LLMAgent
   ├── rag → RAGAgent → LLMAgent
   └── chat → LLMAgent
```

## 配置 n8n Webhook

1. 在 n8n 中创建一个 Webhook 节点
2. 配置 Webhook 路径为 `/webhook/order_email`
3. 在 Webhook 后添加邮件发送节点
4. 将 Webhook URL 配置到 `.env` 文件的 `N8N_WEBHOOK_URL`

Webhook 接收的 JSON 格式：

```json
{
  "order_id": "ORDER123",
  "customer_name": "张三",
  "product": "产品名称",
  "status": "已发货"
}
```

## 开发指南

### 添加新的 Agent

1. 在 `app/agent/` 目录创建新的 Agent 文件
2. 实现 Agent 的 `process` 方法
3. 在 `app/agent/graph.py` 中注册新 Agent 到工作流

### 扩展数据库模型

1. 在 `app/db/models.py` 定义新模型
2. 在 `app/db/crud.py` 添加 CRUD 操作
3. 运行数据库迁移

### 测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_query.py
```

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| POSTGRES_HOST | PostgreSQL 主机 | localhost |
| POSTGRES_PORT | PostgreSQL 端口 | 5432 |
| POSTGRES_DB | 数据库名 | ai_db |
| POSTGRES_USER | 数据库用户 | admin |
| POSTGRES_PASSWORD | 数据库密码 | admin123 |
| REDIS_HOST | Redis 主机 | localhost |
| REDIS_PORT | Redis 端口 | 6379 |
| GEMINI_API_KEY | Gemini API 密钥 | - |
| N8N_WEBHOOK_URL | n8n Webhook URL | - |

## 故障排查

### PostgreSQL 连接失败

- 检查 PostgreSQL 服务是否运行
- 验证 `.env` 中的连接信息
- 确认数据库已创建

### Redis 连接失败

- 检查 Redis 服务是否运行
- 验证 Redis 端口是否正确

### Gemini API 调用失败

- 检查 `GEMINI_API_KEY` 是否正确
- 确认 API 配额是否充足

### LlamaIndex 索引加载失败

- 确认已运行 `python app/rag/ingest.py` 初始化索引
- 检查 PostgreSQL 中 pgvector 扩展是否已安装

## 许可证

MIT License

