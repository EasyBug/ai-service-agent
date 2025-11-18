# Smart Support Agent Frontend

智能客服系统前端项目，基于 Next.js 15、TypeScript、TailwindCSS 和 Shadcn/UI 构建。

## 🚀 技术栈

- **Next.js 15** (App Router)
- **TypeScript**
- **TailwindCSS**
- **Shadcn/UI**
- **Zustand** (状态管理)
- **React Query** (数据获取)
- **Axios** (HTTP 客户端)

## 📋 功能特性

- ✅ 用户登录/登出
- ✅ 智能问答（对接 LangGraph）
- ✅ 订单查询
- ✅ 知识库管理
- ✅ 响应式设计
- ✅ 现代化 UI

## 🛠️ 安装

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

复制 `.env.local.example` 为 `.env.local`：

```bash
cp .env.local.example .env.local
```

编辑 `.env.local`，配置后端 API 地址：

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 [http://localhost:3000](http://localhost:3000)

## 📁 项目结构

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # 根布局
│   ├── page.tsx           # 首页（智能问答）
│   ├── login/             # 登录页
│   ├── order/             # 订单查询页
│   └── rag/               # 知识库管理页
├── components/            # React 组件
│   ├── ui/                # Shadcn/UI 基础组件
│   ├── Sidebar.tsx        # 侧边栏导航
│   ├── ChatBox.tsx        # 聊天框
│   ├── MessageBubble.tsx  # 消息气泡
│   ├── OrderForm.tsx      # 订单查询表单
│   ├── UploadBox.tsx      # 知识库上传
│   └── LoginForm.tsx      # 登录表单
├── lib/                    # 工具函数和配置
│   ├── api.ts             # API 服务封装
│   ├── useAuthStore.ts    # 认证状态管理
│   └── useChatStore.ts    # 聊天状态管理
└── public/                 # 静态资源
```

## 🔐 登录系统

### 当前状态

**注意**：后端目前还没有实现 `/auth/login` 接口。前端已实现登录 UI 和逻辑，但在开发模式下使用模拟登录。

### 开发模式

在开发环境中，前端会使用模拟登录：
- 任意邮箱和密码（至少6位）即可登录
- Token 存储在 localStorage

### 生产模式

需要后端实现以下接口：

```typescript
POST /auth/login
Body: {
  email: string;
  password: string;
}
Response: {
  success: boolean;
  message: string;
  data: {
    token: string;
    email: string;
  }
}
```

## 🔌 API 接口

### 1. 主查询接口

```typescript
POST /query/
Body: {
  query: string;
  thread_id?: string;
}
```

### 2. 订单查询

```typescript
GET /order/query?order_id=ORD-2024-001
```

### 3. 知识库更新

```typescript
POST /rag/update
```

### 4. 健康检查

```typescript
GET /health
```

## 🎨 UI 组件

项目使用 **Shadcn/UI** 组件库，所有组件位于 `components/ui/` 目录。

主要组件：
- Button
- Input
- Card
- Toast
- Label

## 📦 构建

### 开发环境

```bash
npm run dev
```

### 生产构建

```bash
npm run build
npm start
```

## 🔧 配置

### 后端 API 地址

在 `.env.local` 中配置：

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### CORS 配置

确保后端已配置 CORS，允许前端域名访问。

后端配置示例（FastAPI）：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🚨 注意事项

### 1. 认证系统

- 后端需要实现 `/auth/login` 接口
- 前端已实现完整的登录 UI 和状态管理
- 开发模式使用模拟登录

### 2. Token 管理

- Token 存储在 `localStorage`
- 自动添加到请求头：`Authorization: Bearer <token>`
- Token 过期时自动跳转登录页

### 3. 路由保护

- 所有页面（除登录页）都需要认证
- 未登录用户自动重定向到 `/login`

## 📝 开发指南

### 添加新页面

1. 在 `app/` 目录创建新路由
2. 使用 `useAuthStore` 检查登录状态
3. 使用 `Sidebar` 组件添加导航

### 添加新 API

在 `lib/api.ts` 中添加新的 API 方法：

```typescript
export const apiService = {
  // 新接口
  newEndpoint: async (data: any): Promise<any> => {
    return api.post("/new-endpoint", data);
  },
};
```

## 🐛 故障排查

### 1. API 请求失败

- 检查 `.env.local` 中的 `NEXT_PUBLIC_API_BASE_URL`
- 确认后端服务正在运行
- 检查浏览器控制台的错误信息

### 2. 登录问题

- 开发模式：任意邮箱和密码（至少6位）即可
- 生产模式：需要后端实现 `/auth/login` 接口

### 3. CORS 错误

- 确保后端已配置 CORS
- 检查 `allow_origins` 是否包含前端地址

## 📚 相关文档

- [Next.js 文档](https://nextjs.org/docs)
- [TailwindCSS 文档](https://tailwindcss.com/docs)
- [Shadcn/UI 文档](https://ui.shadcn.com)
- [Zustand 文档](https://zustand-demo.pmnd.rs)
- [React Query 文档](https://tanstack.com/query/latest)

## 📄 许可证

MIT

