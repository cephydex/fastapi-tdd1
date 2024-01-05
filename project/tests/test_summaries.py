import json


def test_create_summary(test_app_with_db):
    response = test_app_with_db.post("/summaries/", data=json.dumps({"url": "http://foo.bar"}))

    assert response.status_code == 201
    assert response.json()["url"] == "http://foo.bar"


def test_create_summary_invalid_json(test_app_with_db):
    response = test_app_with_db.post("/summaries/", data=json.dumps({}))

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "url"],
                "msg": "field required",
                "type": "value_error.missing"
            }
        ]
    }


def test_read_summary(test_app_with_db):
    response = test_app_with_db.post("/summaries/", data=json.dumps({"url": "http://foo2.bar"}))
    summary_id = response.json()["id"]

    response = test_app_with_db.get(f"/summaries/{summary_id}/")
    assert response.status_code == 200

    response_dict = response.json()
    assert summary_id == response_dict["id"]
    assert response_dict["url"] == "http://foo2.bar"
    assert response_dict["summary"]
    assert response_dict["created_at"]


def test_read_summary_incorrect_id(test_app_with_db):
    response = test_app_with_db.get("/summaries/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"


def test_read_all_summary(test_app_with_db):
    response = test_app_with_db.post("/summaries/", data=json.dumps({"url": "http://foo_all.bar"}))
    summary_id = response.json()["id"]

    response = test_app_with_db.get("/summaries/")
    assert response.status_code == 200

    response_list = response.json()
    assert len(list(filter(lambda d: d["id"] == summary_id, response_list))) == 1
