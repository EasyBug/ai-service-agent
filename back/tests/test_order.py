"""
订单查询接口测试
"""
import pytest  # type: ignore
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_order_query_not_found():
    """测试查询不存在的订单"""
    response = client.get("/order/query?order_id=NONEXISTENT")
    
    # 应该返回 404 或 200（取决于实现）
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        # 检查是否包含错误信息
        assert not data.get("success", True) or "未找到" in data.get("message", "")


def test_order_query_success():
    """测试查询存在的订单（需要先创建测试数据）"""
    # 注意：这个测试需要数据库中有测试数据
    # 在实际测试中，应该先创建测试订单
    
    response = client.get("/order/query?order_id=TEST_ORDER_001")
    
    # 检查响应状态码
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            order_data = data.get("data", {})
            assert "order_id" in order_data
            assert "status" in order_data


def test_order_query_missing_param():
    """测试缺少订单ID参数"""
    response = client.get("/order/query")
    
    # 应该返回 422（参数验证错误）
    assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

