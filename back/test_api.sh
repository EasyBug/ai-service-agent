#!/bin/bash

# API 测试脚本
BASE_URL="http://localhost:8000"

echo "=========================================="
echo "智能客服系统 API 验证测试"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试函数
test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    
    echo -e "${YELLOW}测试: $name${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✅ 成功 (HTTP $http_code)${NC}"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    else
        echo -e "${RED}❌ 失败 (HTTP $http_code)${NC}"
        echo "$body"
    fi
    echo ""
}

# 1. 健康检查
test_endpoint "健康检查" "GET" "$BASE_URL/health"

# 2. 订单查询 - 存在的订单
test_endpoint "订单查询 (ORD-2024-001)" "GET" "$BASE_URL/order/query?order_id=ORD-2024-001"

# 3. 订单查询 - 不存在的订单
test_endpoint "订单查询 (不存在的订单)" "GET" "$BASE_URL/order/query?order_id=ORD-9999-999"

# 4. RAG 查询 - 产品功能
test_endpoint "RAG 查询 - 产品功能" "POST" "$BASE_URL/query" '{"query": "智能手表有什么功能？"}'

# 5. RAG 查询 - 价格
test_endpoint "RAG 查询 - 价格" "POST" "$BASE_URL/query" '{"query": "智能手表 Pro 多少钱？"}'

# 6. 订单查询（通过主查询接口）
test_endpoint "主查询 - 订单查询" "POST" "$BASE_URL/query" '{"query": "我想查询订单 ORD-2024-001 的状态"}'

# 7. 一般对话
test_endpoint "主查询 - 一般对话" "POST" "$BASE_URL/query" '{"query": "你好，今天天气怎么样？"}'

echo "=========================================="
echo "测试完成！"
echo "=========================================="

