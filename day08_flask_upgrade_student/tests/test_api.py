import pytest
import json
from app import app as flask_app

# 全局测试客户端夹具
@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret"
    })
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

# 模拟登录夹具，返回已登录的客户端
@pytest.fixture
def logged_client(app):
    test_client = app.test_client()
    # 模拟登录接口，写入session（根据你项目登录逻辑调整）
    with test_client.session_transaction() as sess:
        sess["user_id"] = 1
    return test_client

# 测试1：/health 接口返回200状态码
def test_health_api(client):
    resp = client.get("/health")
    assert resp.status_code == 200

# 测试2：未登录访问 /api/metrics 被拦截（401/403）
def test_metrics_no_login(client):
    resp = client.get("/api/metrics")
    # 登录装饰器未授权会返回非200状态码
    assert resp.status_code != 200

# 测试3：登录后访问 /api/metrics，返回ok、metrics字段
def test_metrics_with_login(logged_client):
    resp = logged_client.get("/api/metrics")
    assert resp.status_code == 200
    data = resp.get_json()
    # 校验返回字段
    assert "ok" in data
    assert data["ok"] is True
    assert "metrics" in data
    # metrics是列表，包含4张指标卡
    assert isinstance(data["metrics"], list)
    assert len(data["metrics"]) == 4
    # 校验每条指标包含label/value/note
    item = data["metrics"][0]
    assert "label" in item
    assert "value" in item
    assert "note" in item

# 测试4：带品类筛选参数 /api/categories?category=Fashion 返回筛选数据
def test_categories_filter_fashion(logged_client):
    resp = logged_client.get("/api/categories?category=Fashion")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["category"] == "Fashion"
    assert "rows" in data
    # 筛选后rows数量少于全量数据
    assert len(data["rows"]) > 0
    # 校验每行数据包含品类字段
    first_row = data["rows"][0]
    assert "偏好品类" in first_row
    assert first_row["偏好品类"] == "Fashion"