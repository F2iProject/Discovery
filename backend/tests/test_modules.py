"""CRUD tests for all 11 Discovery modules."""

import pytest
from datetime import date


# Helper to run standard CRUD test for a module
def crud_test(client, auth_headers, path, create_payload, update_payload, expected_fields):
    """Run the 5 standard CRUD operations against a module."""
    # LIST (empty)
    r = client.get(f"/api/{path}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []

    # CREATE
    r = client.post(f"/api/{path}", json=create_payload, headers=auth_headers)
    assert r.status_code == 201, f"Create failed: {r.json()}"
    item = r.json()
    item_id = item["id"]
    for field in expected_fields:
        assert field in item, f"Missing field: {field}"

    # GET
    r = client.get(f"/api/{path}/{item_id}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["id"] == item_id

    # UPDATE
    r = client.patch(f"/api/{path}/{item_id}", json=update_payload, headers=auth_headers)
    assert r.status_code == 200
    for key, value in update_payload.items():
        assert r.json()[key] == value, f"Update failed for {key}"

    # DELETE
    r = client.delete(f"/api/{path}/{item_id}", headers=auth_headers)
    assert r.status_code == 204

    # GET after delete (should 404)
    r = client.get(f"/api/{path}/{item_id}", headers=auth_headers)
    assert r.status_code == 404

    return item_id


class TestDocuments:
    def test_crud(self, client, auth_headers):
        crud_test(client, auth_headers, "documents",
            create_payload={"title": "SOP-001 Pipetting"},
            update_payload={"title": "SOP-001 Pipetting v2", "status": "in_review"},
            expected_fields=["id", "title", "doc_number", "status", "tenant_id"],
        )

    def test_versions(self, client, auth_headers):
        # Create document
        r = client.post("/api/documents", json={"title": "Versioned Doc"}, headers=auth_headers)
        doc_id = r.json()["id"]
        # Create version
        r = client.post(f"/api/documents/{doc_id}/versions", json={
            "version_number": 1, "filename": "doc_v1.pdf"
        }, headers=auth_headers)
        assert r.status_code == 201
        # List versions
        r = client.get(f"/api/documents/{doc_id}/versions", headers=auth_headers)
        assert r.status_code == 200
        assert len(r.json()) == 1


class TestChangeControls:
    def test_crud(self, client, auth_headers):
        crud_test(client, auth_headers, "change-controls",
            create_payload={"title": "Update pipetting procedure"},
            update_payload={"status": "submitted"},
            expected_fields=["id", "title", "change_number", "status"],
        )


class TestCAPAs:
    def test_crud(self, client, auth_headers):
        crud_test(client, auth_headers, "capas",
            create_payload={"title": "Contamination investigation"},
            update_payload={"status": "investigation", "priority": "high"},
            expected_fields=["id", "title", "capa_number", "status", "priority"],
        )

    def test_actions(self, client, auth_headers):
        r = client.post("/api/capas", json={"title": "CAPA with actions"}, headers=auth_headers)
        capa_id = r.json()["id"]
        # Create action
        r = client.post(f"/api/capas/{capa_id}/actions", json={
            "description": "Retrain staff"
        }, headers=auth_headers)
        assert r.status_code == 201
        action_id = r.json()["id"]
        # List actions
        r = client.get(f"/api/capas/{capa_id}/actions", headers=auth_headers)
        assert len(r.json()) == 1
        # Update action -> completed
        r = client.patch(f"/api/capas/{capa_id}/actions/{action_id}", json={
            "status": "completed"
        }, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["completed_at"] is not None


class TestRisks:
    def test_crud(self, client, auth_headers):
        crud_test(client, auth_headers, "risks",
            create_payload={"title": "Chemical spill risk", "severity": 4, "likelihood": 3},
            update_payload={"mitigation": "Install spill containment"},
            expected_fields=["id", "title", "risk_number", "severity", "likelihood", "risk_level"],
        )

    def test_risk_level_computation(self, client, auth_headers):
        r = client.post("/api/risks", json={
            "title": "High risk", "severity": 5, "likelihood": 5
        }, headers=auth_headers)
        assert r.json()["risk_level"] == "critical"

        r = client.post("/api/risks", json={
            "title": "Low risk", "severity": 1, "likelihood": 2
        }, headers=auth_headers)
        assert r.json()["risk_level"] == "low"


class TestTrainings:
    def test_crud(self, client, auth_headers):
        crud_test(client, auth_headers, "trainings",
            create_payload={"title": "Lab Safety Training"},
            update_payload={"status": "active"},
            expected_fields=["id", "title", "status"],
        )

    def test_assignments(self, client, auth_headers, test_user):
        r = client.post("/api/trainings", json={"title": "Assign test"}, headers=auth_headers)
        training_id = r.json()["id"]
        # Create assignment
        r = client.post(f"/api/trainings/{training_id}/assignments", json={
            "user_id": test_user.id
        }, headers=auth_headers)
        assert r.status_code == 201
        assignment_id = r.json()["id"]
        # List
        r = client.get(f"/api/trainings/{training_id}/assignments", headers=auth_headers)
        assert len(r.json()) == 1
        # Complete
        r = client.patch(f"/api/trainings/{training_id}/assignments/{assignment_id}", json={
            "status": "completed"
        }, headers=auth_headers)
        assert r.json()["completed_at"] is not None


class TestNonConformances:
    def test_crud(self, client, auth_headers):
        crud_test(client, auth_headers, "nonconformances",
            create_payload={"title": "Out of spec result"},
            update_payload={"severity": "major", "disposition": "rework"},
            expected_fields=["id", "title", "nc_number", "status", "severity"],
        )


class TestDeviations:
    def test_crud(self, client, auth_headers):
        crud_test(client, auth_headers, "deviations",
            create_payload={"title": "Temperature excursion"},
            update_payload={"status": "under_review"},
            expected_fields=["id", "title", "deviation_number", "status"],
        )


class TestEquipment:
    def test_crud(self, client, auth_headers):
        crud_test(client, auth_headers, "equipment",
            create_payload={"name": "Centrifuge Model X"},
            update_payload={"location": "Lab 3B", "status": "maintenance"},
            expected_fields=["id", "name", "equipment_id", "status"],
        )


class TestCalibrations:
    def test_crud(self, client, auth_headers):
        # Need equipment first
        r = client.post("/api/equipment", json={"name": "pH Meter"}, headers=auth_headers)
        eq_id = r.json()["id"]
        # Now test calibration (note: calibration has no soft delete, so after delete it's gone for real)
        # LIST
        r = client.get("/api/calibrations", headers=auth_headers)
        assert r.status_code == 200
        # CREATE
        r = client.post("/api/calibrations", json={
            "equipment_id": eq_id,
            "calibration_date": "2026-03-16",
            "result": "pass",
            "method": "Two-point buffer",
        }, headers=auth_headers)
        assert r.status_code == 201
        cal_id = r.json()["id"]
        # GET
        r = client.get(f"/api/calibrations/{cal_id}", headers=auth_headers)
        assert r.status_code == 200
        # UPDATE
        r = client.patch(f"/api/calibrations/{cal_id}", json={"result": "adjusted"}, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["result"] == "adjusted"
        # DELETE (hard delete for calibrations)
        r = client.delete(f"/api/calibrations/{cal_id}", headers=auth_headers)
        assert r.status_code == 204


class TestComplaints:
    def test_crud(self, client, auth_headers):
        crud_test(client, auth_headers, "complaints",
            create_payload={"title": "Customer reported defect"},
            update_payload={"status": "under_review", "product": "Widget A"},
            expected_fields=["id", "title", "complaint_number", "status"],
        )


class TestSuppliers:
    def test_crud(self, client, auth_headers):
        crud_test(client, auth_headers, "suppliers",
            create_payload={"name": "Acme Chemicals"},
            update_payload={"qualification_status": "approved", "contact_email": "sales@acme.com"},
            expected_fields=["id", "name", "qualification_status"],
        )
