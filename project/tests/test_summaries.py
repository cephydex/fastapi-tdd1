import json

import pytest


def test_create_summary(test_app_with_db):
    response = test_app_with_db.post(
        "/summaries/", data=json.dumps({"url": "http://foo.bar"})
    )

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
                "type": "value_error.missing",
            }
        ]
    }

    response = test_app_with_db.post(
        "/summaries/", data=json.dumps({"url": "invalid://url"})
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "URL scheme not permitted"


def test_read_summary(test_app_with_db):
    response = test_app_with_db.post(
        "/summaries/", data=json.dumps({"url": "http://foo2.bar"})
    )
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

    response = test_app_with_db.get("/summaries/0/")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["path", "id"],
                "msg": "ensure this value is greater than 0",
                "type": "value_error.number.not_gt",
                "ctx": {"limit_value": 0},
            }
        ]
    }


def test_read_all_summary(test_app_with_db):
    response = test_app_with_db.post(
        "/summaries/", data=json.dumps({"url": "http://foo_all.bar"})
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.get("/summaries/")
    assert response.status_code == 200

    response_list = response.json()
    assert len(list(filter(lambda d: d["id"] == summary_id, response_list))) == 1


def test_remove_summary(test_app_with_db):
    response = test_app_with_db.post(
        "/summaries/", data=json.dumps({"url": "https://foo_all.bar"})
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.delete(f"/summaries/{summary_id}/")
    assert response.status_code == 200
    assert response.json() == {"id": summary_id, "url": "https://foo_all.bar"}


def test_remove_summary_incorrect_id(test_app_with_db):
    response = test_app_with_db.delete("/summaries/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"


def test_update_summary(test_app_with_db):
    response = test_app_with_db.post(
        "/summaries/", data=json.dumps({"url": "https://foo_all.bar"})
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.put(
        f"/summaries/{summary_id}/",
        data=json.dumps({"url": "https://foo_all.bar", "summary": "updated!"}),
    )
    assert response.status_code == 200

    response_dict = response.json()
    assert response_dict["id"] == summary_id
    assert response_dict["url"] == "https://foo_all.bar"
    assert response_dict["summary"] == "updated!"
    assert response_dict["created_at"]


@pytest.mark.parametrize(
    "summary_id, payload, status_code, detail",
    [
        [
            999,
            {"url": "http://foo_all.bar", "summary": "updated!"},
            404,
            "Summary not found",
        ],
        [
            0,
            {"url": "https://foo.bar", "summary": "updated!"},
            422,
            [
                {
                    "loc": ["path", "id"],
                    "msg": "ensure this value is greater than 0",
                    "type": "value_error.number.not_gt",
                    "ctx": {"limit_value": 0},
                }
            ],
        ],
        [
            1,
            {},
            422,
            [
                {
                    "loc": ["body", "url"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
                {
                    "loc": ["body", "summary"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
            ],
        ],
        [
            1,
            {"url": "https://foo.bar"},
            422,
            [
                {
                    "loc": ["body", "summary"],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ],
        ],
    ],
)
def test_update_summary_invalid(
    test_app_with_db, summary_id, payload, status_code, detail
):
    response = test_app_with_db.put(
        f"/summaries/{summary_id}/", data=json.dumps(payload)
    )
    assert response.status_code == status_code
    assert response.json()["detail"] == detail


def test_update_summary_invalid_url(test_app):
    response = test_app.put(
        "/summaries/1/",
        data=json.dumps({"url": "invalid://url", "summary": "updated!"}),
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "URL scheme not permitted"


# def test_update_summary_incorrect_id(test_app_with_db):
#     response = test_app_with_db.put(
#         f"/summaries/999/",
#         data=json.dumps({"url": "http://foo_all.bar", "summary": "updated!"})
#     )
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Summary not found"

#     response = test_app_with_db.put(
#         f"/summaries/0/",
#         data=json.dumps({"url": "https://foo.bar", "summary": "updated!"})
#     )
#     assert response.status_code == 422
#     assert response.json() == {
#         "detail": [
#             {
#                 "loc": ["path", "id"],
#                 "msg": "ensure this value is greater than 0",
#                 "type": "value_error.number.not_gt",
#                 "ctx": {"limit_value": 0},
#             }
#         ]
#     }


# def test_update_summary_invalid_json(test_app_with_db):
#     response = test_app_with_db.post(
#         "/summaries/", data=json.dumps({"url": "https://foo_all.bar"})
#     )
#     summary_id = response.json()["id"]

#     response = test_app_with_db.put(
#         f"/summaries/{summary_id}/",
#         data=json.dumps({})
#     )
#     assert response.status_code == 422
#     assert response.json() == {
#         "detail": [
#             {
#                 "loc": ["body", "url"],
#                 "msg": "field required",
#                 "type": "value_error.missing",
#             },
#             {
#                 "loc": ["body", "summary"],
#                 "msg": "field required",
#                 "type": "value_error.missing",
#             }
#         ]
#     }


# def test_update_summary_invalid_keys(test_app_with_db):
#     response = test_app_with_db.post(
#         "/summaries/", data=json.dumps({"url": "https://foo_all.bar"})
#     )
#     summary_id = response.json()["id"]

#     response = test_app_with_db.put(
#         f"/summaries/{summary_id}/",
#         data=json.dumps({"url": "http://foo_all.bar",})
#     )
#     assert response.status_code == 422
#     assert response.json() == {
#         "detail": [
#             {
#                 "loc": ["body", "summary"],
#                 "msg": "field required",
#                 "type": "value_error.missing",
#             }
#         ]
#     }

#     response = test_app_with_db.put(
#         f"/summaries/{summary_id}/",
#         data=json.dumps({"url": "invalid://url", "summary": "updated!"})
#     )
#     assert response.status_code == 422
#     assert response.json()["detail"][0]["msg"] == "URL scheme not permitted"
