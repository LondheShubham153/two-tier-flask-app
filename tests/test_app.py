from unittest.mock import MagicMock

import pytest

import app as app_module


@pytest.fixture
def client(monkeypatch):
    conn = MagicMock()
    cur = conn.cursor.return_value.__enter__.return_value
    cur.fetchall.return_value = (("hello",), ("<b>world</b>",))
    monkeypatch.setattr(app_module, "get_conn", lambda: conn)
    monkeypatch.setattr(app_module, "_db_ready", False)
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()
    client.cur = cur
    return client


def test_health_does_not_need_db(monkeypatch):
    def boom():
        raise RuntimeError("db down")

    monkeypatch.setattr(app_module, "get_conn", boom)
    res = app_module.app.test_client().get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_index_lists_messages_and_escapes_html(client):
    res = client.get("/")
    body = res.get_data(as_text=True)
    assert res.status_code == 200
    assert "<p>hello</p>" in body
    assert "&lt;b&gt;world&lt;/b&gt;" in body
    assert "Served by" in body


def test_submit_inserts_and_returns_json(client):
    res = client.post("/submit", data={"new_message": "hi"})
    assert res.status_code == 200
    assert res.get_json() == {"message": "hi"}
    client.cur.execute.assert_any_call(
        "INSERT INTO messages (message) VALUES (%s)", ["hi"]
    )
