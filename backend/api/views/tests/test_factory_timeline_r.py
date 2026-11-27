from datetime import datetime, timezone
from uuid import uuid4

import pytest
from freezegun import freeze_time

from api.models import Document, Factory, FollowUp, Image, ReportRecord


pytestmark = pytest.mark.django_db


def _create_factory(display_number=123):
    return Factory.objects.create(
        name="timeline_test_factory",
        lat=24.0,
        lng=121.0,
        status_time=datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        display_number=display_number,
    )


def test_get_factory_timeline_full(client):
    factory = _create_factory(display_number=456)

    # Documents & FollowUps
    with freeze_time("2023-01-12T00:00:00Z"):
        doc1 = Document.objects.create(factory=factory, code=1001)
    with freeze_time("2023-01-17T00:00:00Z"):
        doc2 = Document.objects.create(factory=factory, code=1002, display_status=1)

    with freeze_time("2023-01-15T10:30:00Z"):
        transition1 = FollowUp.objects.create(
            document=doc1,
            note="已檢舉 -> 已排程稽查",
            for_user=False,
        )
    with freeze_time("2023-01-16T08:00:00Z"):
        # Internal note without " -> " must be excluded from both lists
        FollowUp.objects.create(
            document=doc1,
            note="內部追蹤備註",
            for_user=False,
        )
    with freeze_time("2023-01-18T12:00:00Z"):
        # Transition on second document should interleave chronologically
        transition2 = FollowUp.objects.create(
            document=doc2,
            note="已排程稽查 -> 已勒令停工",
            for_user=False,
        )
    with freeze_time("2023-01-20T14:00:00Z"):
        # for_user=True note containing " -> " stays in follow_ups_for_user only
        followup_user = FollowUp.objects.create(
            document=doc1,
            note="進度回報內容 -> 縣府已回覆",
            for_user=True,
        )

    # ReportRecords: POST excluded, UPDATE and POST_IMAGE included, PII stripped
    with freeze_time("2023-01-01T01:00:00Z"):
        ReportRecord.objects.create(
            factory=factory,
            action_type="POST",
            action_body={"name": "初始回報", "contact": "0900-000-000"},
            others="首次建立",
        )
    with freeze_time("2023-01-10T08:00:00Z"):
        update_report = ReportRecord.objects.create(
            factory=factory,
            action_type="UPDATE",
            action_body={
                "name": "更新工廠名",
                "factory_type": "2-1",
                "contact": "0912-345-678",
                "nickname": "檢舉人",
            },
            others="備註",
        )
    with freeze_time("2023-01-11T09:00:00Z"):
        image_report = ReportRecord.objects.create(
            factory=factory,
            action_type="POST_IMAGE",
            action_body={"url": "https://i.imgur.com/img1.jpg", "deletehash": "secret"},
            others="",
        )

    # Images: group by local (Asia/Taipei, UTC+8) created_at date, NOT orig_time
    # 2023-01-01T15:00:00Z == 2023-01-01 23:00+08:00 (2023-01-01)
    # 2023-01-01T17:00:00Z == 2023-01-02 01:00+08:00 (2023-01-02)
    with freeze_time("2023-01-01T10:00:00Z"):
        img1 = Image.objects.create(
            factory=factory,
            image_path="https://i.imgur.com/day1_a.jpg",
            orig_time=datetime(2022, 6, 1, 12, 0, 0, tzinfo=timezone.utc),
        )
    with freeze_time("2023-01-01T15:00:00Z"):
        img2 = Image.objects.create(
            factory=factory,
            image_path="https://i.imgur.com/day1_b.jpg",
            orig_time=datetime(2022, 7, 1, 12, 0, 0, tzinfo=timezone.utc),
        )
    with freeze_time("2023-01-01T17:00:00Z"):
        img3 = Image.objects.create(
            factory=factory,
            image_path="https://i.imgur.com/day2_a.jpg",
            orig_time=datetime(2022, 6, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

    # Another factory's data must not leak
    other_factory = _create_factory(display_number=999)
    other_doc = Document.objects.create(factory=other_factory, code=9999)
    FollowUp.objects.create(document=other_doc, note="已檢舉 -> 已拆除", for_user=False)
    FollowUp.objects.create(document=other_doc, note="別間工廠的回覆", for_user=True)
    ReportRecord.objects.create(
        factory=other_factory,
        action_type="UPDATE",
        action_body={"name": "other"},
        others="other",
    )
    Image.objects.create(factory=other_factory, image_path="https://i.imgur.com/other.jpg")

    resp = client.get(f"/api/factories/{factory.id}/timeline")
    assert resp.status_code == 200
    data = resp.json()

    assert data["factory_id"] == str(factory.id)
    assert data["display_number"] == 456

    # Each filed document is a 發公文檢舉 event; the 公文號 (code) stays private
    assert data["documents"] == [
        {"id": doc1.id, "created_at": "2023-01-12T08:00:00+08:00", "display_status": "已檢舉"},
        {"id": doc2.id, "created_at": "2023-01-17T08:00:00+08:00", "display_status": "已排程稽查"},
    ]

    assert len(data["status_transitions"]) == 2
    assert data["status_transitions"][0]["id"] == transition1.id
    assert data["status_transitions"][0]["from_status"] == "已檢舉"
    assert data["status_transitions"][0]["to_status"] == "已排程稽查"
    assert data["status_transitions"][0]["document_id"] == doc1.id
    assert data["status_transitions"][1]["id"] == transition2.id
    assert data["status_transitions"][1]["from_status"] == "已排程稽查"
    assert data["status_transitions"][1]["to_status"] == "已勒令停工"
    assert data["status_transitions"][1]["document_id"] == doc2.id

    assert [r["id"] for r in data["user_reports"]] == [update_report.id, image_report.id]
    assert data["user_reports"][0]["action_type"] == "UPDATE"
    assert data["user_reports"][0]["action_body"] == {
        "name": "更新工廠名",
        "factory_type": "2-1",
    }
    assert data["user_reports"][0]["others"] == "備註"
    assert data["user_reports"][1]["action_type"] == "POST_IMAGE"
    assert data["user_reports"][1]["action_body"] == {
        "url": "https://i.imgur.com/img1.jpg",
    }

    assert len(data["follow_ups_for_user"]) == 1
    assert data["follow_ups_for_user"][0]["id"] == followup_user.id
    assert data["follow_ups_for_user"][0]["note"] == "進度回報內容 -> 縣府已回覆"

    assert len(data["image_batches"]) == 2
    assert data["image_batches"][0]["date"] == "2023-01-01"
    assert data["image_batches"][0]["count"] == 2
    assert [img["id"] for img in data["image_batches"][0]["images"]] == [
        str(img1.id),
        str(img2.id),
    ]
    assert data["image_batches"][0]["images"][0]["image_path"] == "https://i.imgur.com/day1_a.jpg"
    assert data["image_batches"][0]["images"][0]["url"] == "https://i.imgur.com/day1_a.jpg"
    assert "created_at" in data["image_batches"][0]["images"][0]

    assert data["image_batches"][1]["date"] == "2023-01-02"
    assert data["image_batches"][1]["count"] == 1
    assert [img["id"] for img in data["image_batches"][1]["images"]] == [str(img3.id)]


def test_get_factory_timeline_empty(client):
    factory = _create_factory(display_number=789)

    resp = client.get(f"/api/factories/{factory.id}/timeline")
    assert resp.status_code == 200
    assert resp.json() == {
        "factory_id": str(factory.id),
        "display_number": 789,
        "documents": [],
        "status_transitions": [],
        "user_reports": [],
        "follow_ups_for_user": [],
        "image_batches": [],
    }


def test_get_factory_timeline_excludes_soft_deleted_records(client):
    factory = _create_factory(display_number=321)
    active_doc = Document.objects.create(factory=factory, code=2001)
    deleted_doc = Document.objects.create(factory=factory, code=2002)

    deleted_followup = FollowUp.objects.create(
        document=active_doc, note="已檢舉 -> 已拆除", for_user=False
    )
    deleted_followup.delete()

    FollowUp.objects.create(
        document=deleted_doc, note="已檢舉 -> 已排程稽查", for_user=False
    )
    FollowUp.objects.create(
        document=deleted_doc, note="已刪除公文的回覆", for_user=True
    )
    deleted_doc.delete()

    deleted_report = ReportRecord.objects.create(
        factory=factory, action_type="UPDATE", action_body={"name": "deleted"}, others="x"
    )
    deleted_report.delete()

    deleted_image = Image.objects.create(
        factory=factory, image_path="https://i.imgur.com/deleted.jpg"
    )
    deleted_image.delete()

    resp = client.get(f"/api/factories/{factory.id}/timeline")
    assert resp.status_code == 200
    data = resp.json()
    assert [d["id"] for d in data["documents"]] == [active_doc.id]
    assert data["status_transitions"] == []
    assert data["user_reports"] == []
    assert data["follow_ups_for_user"] == []
    assert data["image_batches"] == []


def test_get_factory_timeline_not_found_and_invalid_id(client):
    resp_missing = client.get(f"/api/factories/{uuid4()}/timeline")
    assert resp_missing.status_code == 404

    resp_invalid = client.get("/api/factories/not-a-valid-uuid/timeline")
    assert resp_invalid.status_code == 400

    # Soft-deleted factory also returns 404
    factory = _create_factory(display_number=654)
    factory.delete()
    resp_deleted = client.get(f"/api/factories/{factory.id}/timeline")
    assert resp_deleted.status_code == 404


def test_get_factory_timeline_query_count(client, django_assert_max_num_queries):
    factory = _create_factory(display_number=555)
    for i in range(4):
        doc = Document.objects.create(factory=factory, code=3000 + i)
        FollowUp.objects.create(document=doc, note="已檢舉 -> 已排程稽查", for_user=False)
        FollowUp.objects.create(document=doc, note=f"回覆 {i}", for_user=True)
        ReportRecord.objects.create(
            factory=factory, action_type="UPDATE", action_body={"name": f"n{i}"}, others=f"o{i}"
        )
        Image.objects.create(factory=factory, image_path="https://i.imgur.com/q{}.jpg".format(i))

    with django_assert_max_num_queries(5):
        resp = client.get(f"/api/factories/{factory.id}/timeline")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["status_transitions"]) == 4
    assert len(data["follow_ups_for_user"]) == 4
    assert len(data["user_reports"]) == 4
    assert sum(b["count"] for b in data["image_batches"]) == 4
