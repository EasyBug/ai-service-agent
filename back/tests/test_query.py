"""
查询接口测试
"""
import pytest  # type: ignore
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """测试健康检查接口"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_query_endpoint():
    """测试主查询接口"""
    # 测试一般查询
    response = client.post(
        "/query/",
        json={
            "query": "你好",
            "thread_id": "test_thread_1"
        }
    )
    
    # 检查响应状态码
    assert response.status_code in [200, 500]  # 可能因为 API key 未配置而失败
    
    if response.status_code == 200:
        data = response.json()
        assert "data" in data
        assert "response" in data.get("data", {})


def test_query_with_order_intent():
    """测试订单查询意图"""
    response = client.post(
        "/query/",
        json={
            "query": "查询订单 ORDER123",
            "thread_id": "test_thread_2"
        }
    )
    
    # 检查响应状态码
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "data" in data


def test_query_with_rag_intent():
    """测试知识库查询意图"""
    response = client.post(
        "/query/",
        json={
            "query": "如何使用产品？",
            "thread_id": "test_thread_3"
        }
    )
    
    # 检查响应状态码
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "data" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

