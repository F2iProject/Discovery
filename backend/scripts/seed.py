"""Seed script: creates a default tenant, admin user, and sample data for all 11 modules.

Usage: python -m scripts.seed
"""

import sys
import os
from datetime import date, datetime, timezone

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.tenant import Tenant
from app.models.user import User
from app.models.document import Document, DocumentVersion
from app.models.change_control import ChangeControl
from app.models.capa import CAPA, CAPAAction
from app.models.risk import Risk
from app.models.training import Training, TrainingAssignment
from app.models.nonconformance import NonConformance
from app.models.deviation import Deviation
from app.models.equipment import Equipment
from app.models.calibration import CalibrationRecord
from app.models.complaint import Complaint
from app.models.supplier import Supplier
from app.models.mixins import generate_uuid
from app.core.security import get_password_hash

# Import all models so tables are registered
from app.models import *  # noqa


def seed():
    """Create default tenant, admin user, and sample data."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if any tenant exists
        existing = db.query(Tenant).first()
        if existing:
            print(f"Database already seeded. Tenant: {existing.name}")
            return

        # ── Tenant ──────────────────────────────────────────────
        tenant = Tenant(id=generate_uuid(), name="My Lab", slug="my-lab")
        db.add(tenant)
        db.flush()
        tid = tenant.id

        # ── Users ───────────────────────────────────────────────
        admin = User(
            id=generate_uuid(),
            email="admin@lab.dev",
            hashed_password=get_password_hash("discovery"),
            full_name="Lab Admin",
            role="admin",
            is_active=True,
            tenant_id=tid,
        )
        scientist = User(
            id=generate_uuid(),
            email="scientist@lab.dev",
            hashed_password=get_password_hash("discovery"),
            full_name="Dr. Jane Chen",
            role="member",
            is_active=True,
            tenant_id=tid,
        )
        tech = User(
            id=generate_uuid(),
            email="tech@lab.dev",
            hashed_password=get_password_hash("discovery"),
            full_name="Marcus Rivera",
            role="member",
            is_active=True,
            tenant_id=tid,
        )
        db.add_all([admin, scientist, tech])
        db.flush()

        # ── Documents ──────────────────────────────────────────
        docs = [
            Document(
                id=generate_uuid(), tenant_id=tid, created_by=admin.id,
                title="Standard Operating Procedure — Pipetting",
                doc_number="DOC-0001", doc_type="sop", status="approved",
                description="Covers single-channel and multi-channel pipetting technique, calibration verification, and tip disposal.",
                current_version=2,
            ),
            Document(
                id=generate_uuid(), tenant_id=tid, created_by=scientist.id,
                title="Protocol — Cell Culture Passage",
                doc_number="DOC-0002", doc_type="protocol", status="approved",
                description="Step-by-step protocol for passaging adherent mammalian cell lines.",
                current_version=1,
            ),
            Document(
                id=generate_uuid(), tenant_id=tid, created_by=scientist.id,
                title="Method — HPLC Analysis of Active Ingredient",
                doc_number="DOC-0003", doc_type="method", status="in_review",
                description="Reverse-phase HPLC method for quantitation of active pharmaceutical ingredient in tablet formulations.",
                current_version=1,
            ),
            Document(
                id=generate_uuid(), tenant_id=tid, created_by=admin.id,
                title="Form — Equipment Cleaning Log",
                doc_number="DOC-0004", doc_type="form", status="draft",
                description="Daily cleaning log template for shared laboratory equipment.",
                current_version=1,
            ),
            Document(
                id=generate_uuid(), tenant_id=tid, created_by=admin.id,
                title="Policy — Lab Safety and PPE Requirements",
                doc_number="DOC-0005", doc_type="policy", status="approved",
                description="Mandatory PPE requirements, chemical handling procedures, and emergency response protocols.",
                current_version=3,
            ),
        ]
        db.add_all(docs)
        db.flush()

        # Document versions for the pipetting SOP
        db.add_all([
            DocumentVersion(
                id=generate_uuid(), document_id=docs[0].id,
                version_number=1, filename="SOP_Pipetting_v1.pdf",
                change_summary="Initial release", uploaded_by=admin.id,
            ),
            DocumentVersion(
                id=generate_uuid(), document_id=docs[0].id,
                version_number=2, filename="SOP_Pipetting_v2.pdf",
                change_summary="Added multi-channel pipetting section and calibration check frequency",
                uploaded_by=scientist.id,
            ),
        ])

        # ── Equipment ──────────────────────────────────────────
        equipment = [
            Equipment(
                id=generate_uuid(), tenant_id=tid, added_by=admin.id,
                name="Eppendorf Centrifuge 5425",
                equipment_id="EQ-0001", category="Centrifuge",
                manufacturer="Eppendorf", model="5425 R",
                serial_number="EP-2024-8847", location="Lab 1 — Bench A",
                status="active",
            ),
            Equipment(
                id=generate_uuid(), tenant_id=tid, added_by=admin.id,
                name="Agilent 1260 Infinity II HPLC",
                equipment_id="EQ-0002", category="Chromatography",
                manufacturer="Agilent", model="1260 Infinity II",
                serial_number="AG-2023-5512", location="Analytical Lab",
                status="active",
            ),
            Equipment(
                id=generate_uuid(), tenant_id=tid, added_by=tech.id,
                name="Mettler Toledo XPR Analytical Balance",
                equipment_id="EQ-0003", category="Balance",
                manufacturer="Mettler Toledo", model="XPR206DR",
                serial_number="MT-2024-1190", location="Weighing Room",
                status="active",
            ),
            Equipment(
                id=generate_uuid(), tenant_id=tid, added_by=tech.id,
                name="Thermo Fisher Biological Safety Cabinet",
                equipment_id="EQ-0004", category="Safety Cabinet",
                manufacturer="Thermo Fisher", model="1300 Series A2",
                serial_number="TF-2022-7743", location="Cell Culture Suite",
                status="active",
            ),
            Equipment(
                id=generate_uuid(), tenant_id=tid, added_by=admin.id,
                name="VWR Incubator (CO₂)",
                equipment_id="EQ-0005", category="Incubator",
                manufacturer="VWR", model="Symphony 5.3A",
                serial_number="VWR-2023-3301", location="Cell Culture Suite",
                status="maintenance", notes="Annual PM scheduled for next week",
            ),
            Equipment(
                id=generate_uuid(), tenant_id=tid, added_by=tech.id,
                name="Gilson Pipetman P200 (Retired)",
                equipment_id="EQ-0006", category="Pipette",
                manufacturer="Gilson", model="Pipetman P200",
                serial_number="GIL-2019-0042", location="Storage",
                status="retired", notes="Failed calibration check, replaced by P200L",
            ),
        ]
        db.add_all(equipment)
        db.flush()

        # ── Calibrations ───────────────────────────────────────
        db.add_all([
            CalibrationRecord(
                id=generate_uuid(), tenant_id=tid, performed_by=tech.id,
                equipment_id=equipment[2].id,  # Balance
                calibration_date=date(2026, 2, 15),
                next_due=date(2026, 8, 15),
                interval_days=180, result="pass",
                method="ASTM E898 — two-point calibration with NIST-traceable weights",
                certificate_ref="CAL-2026-0221",
            ),
            CalibrationRecord(
                id=generate_uuid(), tenant_id=tid, performed_by=tech.id,
                equipment_id=equipment[1].id,  # HPLC
                calibration_date=date(2026, 1, 10),
                next_due=date(2027, 1, 10),
                interval_days=365, result="pass",
                method="System suitability per USP <621>",
                certificate_ref="CAL-2026-0088",
            ),
            CalibrationRecord(
                id=generate_uuid(), tenant_id=tid, performed_by=tech.id,
                equipment_id=equipment[5].id,  # Retired pipette
                calibration_date=date(2025, 11, 3),
                next_due=date(2026, 5, 3),
                interval_days=180, result="fail",
                method="Gravimetric per ISO 8655",
                notes="Deviation >2% at 100µL and 200µL. Pipette retired.",
            ),
        ])

        # ── Suppliers ──────────────────────────────────────────
        suppliers = [
            Supplier(
                id=generate_uuid(), tenant_id=tid, added_by=admin.id,
                name="Sigma-Aldrich (Merck)",
                contact_name="Regional Account Manager",
                contact_email="orders@sigmaaldrich.com",
                website="https://www.sigmaaldrich.com",
                supplies="Reagents, solvents, reference standards",
                qualification_status="approved",
            ),
            Supplier(
                id=generate_uuid(), tenant_id=tid, added_by=admin.id,
                name="Fisher Scientific",
                contact_name="Lab Supplies Team",
                contact_email="support@fishersci.com",
                website="https://www.fishersci.com",
                supplies="Consumables, plasticware, PPE, general lab supplies",
                qualification_status="approved",
            ),
            Supplier(
                id=generate_uuid(), tenant_id=tid, added_by=admin.id,
                name="Agilent Technologies",
                contact_name="Service & Support",
                contact_email="service@agilent.com",
                website="https://www.agilent.com",
                supplies="HPLC columns, replacement parts, service contracts",
                qualification_status="approved",
            ),
            Supplier(
                id=generate_uuid(), tenant_id=tid, added_by=tech.id,
                name="BioRad Laboratories",
                contact_email="orders@bio-rad.com",
                website="https://www.bio-rad.com",
                supplies="Electrophoresis, protein assay kits",
                qualification_status="pending",
                notes="Evaluating for new Western blot workflow",
            ),
        ]
        db.add_all(suppliers)
        db.flush()

        # ── Risks ──────────────────────────────────────────────
        risks = [
            Risk(
                id=generate_uuid(), tenant_id=tid, created_by=scientist.id,
                title="Chemical spill in analytical lab",
                risk_number="RISK-0001", status="active",
                category="Safety", description="Concentrated acid or solvent spill during sample preparation.",
                severity=4, likelihood=2, risk_level="medium",
                mitigation="Spill kits stationed at each bench. Annual spill response training required.",
            ),
            Risk(
                id=generate_uuid(), tenant_id=tid, created_by=scientist.id,
                title="Cross-contamination of cell cultures",
                risk_number="RISK-0002", status="active",
                category="Quality", description="Mycoplasma or bacterial contamination during cell passage.",
                severity=5, likelihood=3, risk_level="high",
                mitigation="Monthly mycoplasma testing. Dedicated media per cell line. BSC decontamination between lines.",
            ),
            Risk(
                id=generate_uuid(), tenant_id=tid, created_by=admin.id,
                title="Data integrity loss — lab notebook",
                risk_number="RISK-0003", status="draft",
                category="Data Integrity", description="Handwritten lab notebooks could be lost, damaged, or illegible.",
                severity=3, likelihood=3, risk_level="medium",
                mitigation="Considering transition to electronic lab notebooks.",
            ),
            Risk(
                id=generate_uuid(), tenant_id=tid, created_by=scientist.id,
                title="HPLC column degradation",
                risk_number="RISK-0004", status="mitigated",
                category="Equipment", description="Gradual loss of column efficiency leading to inaccurate results.",
                severity=3, likelihood=2, risk_level="medium",
                mitigation="Column performance tracked via system suitability. Replacement at >10% efficiency loss.",
            ),
        ]
        db.add_all(risks)

        # ── CAPAs ──────────────────────────────────────────────
        capa1 = CAPA(
            id=generate_uuid(), tenant_id=tid, created_by=admin.id,
            title="Incorrect buffer pH in batch 2026-003",
            capa_number="CAPA-0001", capa_type="corrective",
            status="implemented", priority="high",
            description="pH meter reading was 0.3 units off due to expired calibration buffer. Batch released with out-of-spec pH.",
            root_cause="Calibration buffer expired 2 weeks prior. No expiration check in procedure.",
            source="nc", target_date=date(2026, 3, 1),
        )
        capa2 = CAPA(
            id=generate_uuid(), tenant_id=tid, created_by=scientist.id,
            title="Recurring contamination in incubator 5",
            capa_number="CAPA-0002", capa_type="preventive",
            status="investigation", priority="medium",
            description="Third contamination event in 6 months in the same incubator.",
            source="deviation",
            target_date=date(2026, 4, 15),
        )
        capa3 = CAPA(
            id=generate_uuid(), tenant_id=tid, created_by=admin.id,
            title="Training gap — new HPLC method",
            capa_number="CAPA-0003", capa_type="preventive",
            status="open", priority="low",
            description="Two analysts ran the new HPLC method without completing training. No impact on results, but procedure was not followed.",
            source="audit",
        )
        db.add_all([capa1, capa2, capa3])
        db.flush()

        db.add_all([
            CAPAAction(
                id=generate_uuid(), capa_id=capa1.id,
                description="Add expiration date check to pH meter calibration SOP",
                action_type="corrective", status="completed",
                assigned_to=admin.id,
                completed_at=datetime(2026, 2, 20, tzinfo=timezone.utc),
            ),
            CAPAAction(
                id=generate_uuid(), capa_id=capa1.id,
                description="Retrain all analysts on buffer preparation procedure",
                action_type="preventive", status="in_progress",
                assigned_to=scientist.id,
            ),
            CAPAAction(
                id=generate_uuid(), capa_id=capa2.id,
                description="Deep clean incubator and replace HEPA filter",
                action_type="correction", status="completed",
                assigned_to=tech.id,
                completed_at=datetime(2026, 3, 5, tzinfo=timezone.utc),
            ),
            CAPAAction(
                id=generate_uuid(), capa_id=capa2.id,
                description="Implement weekly water tray decontamination schedule",
                action_type="preventive", status="open",
                assigned_to=tech.id,
            ),
        ])

        # ── Non-Conformances ───────────────────────────────────
        db.add_all([
            NonConformance(
                id=generate_uuid(), tenant_id=tid, reported_by=tech.id,
                title="Out-of-spec pH in buffer lot 2026-003",
                nc_number="NC-0001", status="closed",
                severity="major", category="Manufacturing",
                description="Buffer pH measured at 7.7 instead of target 7.4 ± 0.1. Traced to expired calibration standards.",
                disposition="rework",
                disposition_rationale="Buffer was re-prepared with fresh reagents and verified within specification.",
                capa_id=capa1.id,
            ),
            NonConformance(
                id=generate_uuid(), tenant_id=tid, reported_by=scientist.id,
                title="Reagent received without Certificate of Analysis",
                nc_number="NC-0002", status="under_review",
                severity="minor", category="Incoming Inspection",
                description="Shipment of sodium chloride from Sigma-Aldrich arrived without CoA. Lot: SLCH1234.",
                disposition="use_as_is",
                disposition_rationale="CoA obtained from supplier website. Specs confirmed within acceptance criteria.",
            ),
            NonConformance(
                id=generate_uuid(), tenant_id=tid, reported_by=tech.id,
                title="Cracked flask found after autoclave cycle",
                nc_number="NC-0003", status="open",
                severity="minor", category="Equipment",
                description="500mL Erlenmeyer flask cracked during autoclave cycle 2026-0312. No media contamination.",
            ),
        ])

        # ── Deviations ─────────────────────────────────────────
        db.add_all([
            Deviation(
                id=generate_uuid(), tenant_id=tid, reported_by=scientist.id,
                title="Temperature excursion in cold room",
                deviation_number="DEV-0001", deviation_type="unplanned",
                status="closed",
                description="Cold room temperature rose to 12°C for approximately 2 hours due to compressor fault.",
                justification="N/A — unplanned event",
                resolution="Compressor repaired. Affected samples assessed — no impact on stability study specimens.",
                affected_document_id=docs[0].id,
            ),
            Deviation(
                id=generate_uuid(), tenant_id=tid, reported_by=scientist.id,
                title="Used alternate HPLC column for method validation",
                deviation_number="DEV-0002", deviation_type="planned",
                status="approved",
                description="Primary column (Agilent Poroshell 120) on backorder. Used equivalent Waters Symmetry C18 column.",
                justification="Columns have equivalent selectivity per USP L1 classification. System suitability criteria still met.",
                resolution="Method performed equivalently. Results included in validation report.",
            ),
            Deviation(
                id=generate_uuid(), tenant_id=tid, reported_by=tech.id,
                title="Sample stored at room temperature overnight",
                deviation_number="DEV-0003", deviation_type="unplanned",
                status="under_review",
                description="Stability samples left on bench overnight instead of being returned to 2-8°C storage.",
                capa_id=capa2.id,
            ),
        ])

        # ── Change Controls ────────────────────────────────────
        db.add_all([
            ChangeControl(
                id=generate_uuid(), tenant_id=tid, requested_by=admin.id,
                title="Update pipetting SOP to include multi-channel technique",
                change_number="CC-0001", status="approved",
                change_type="document",
                description="Adding Section 5.3 covering multi-channel pipetting and new calibration check frequency.",
                justification="Lab acquired multi-channel pipettes. Existing SOP only covers single-channel.",
                impact_assessment="Low impact. Training update required for 3 analysts.",
                document_id=docs[0].id,
            ),
            ChangeControl(
                id=generate_uuid(), tenant_id=tid, requested_by=scientist.id,
                title="Replace HPLC autosampler module",
                change_number="CC-0002", status="under_review",
                change_type="equipment",
                description="Upgrade Agilent 1260 autosampler from G7129A to G7129B for improved carryover performance.",
                justification="Current autosampler shows >0.1% carryover on low-level samples.",
                impact_assessment="Method revalidation required. Estimated 2 weeks downtime.",
            ),
            ChangeControl(
                id=generate_uuid(), tenant_id=tid, requested_by=admin.id,
                title="Switch cleaning agent for shared equipment",
                change_number="CC-0003", status="draft",
                change_type="process",
                description="Transition from 70% IPA to Virkon for daily bench cleaning.",
                justification="Virkon is more effective against mycoplasma and common lab contaminants.",
            ),
        ])

        # ── Training ───────────────────────────────────────────
        training1 = Training(
            id=generate_uuid(), tenant_id=tid, created_by=admin.id,
            title="Lab Safety and PPE Requirements",
            description="Covers mandatory PPE, chemical handling, fire extinguisher locations, and emergency procedures.",
            status="active", document_id=docs[4].id,
        )
        training2 = Training(
            id=generate_uuid(), tenant_id=tid, created_by=scientist.id,
            title="HPLC Method — Active Ingredient Quantitation",
            description="Training on the reverse-phase HPLC method including sample prep, system suitability, and data review.",
            status="active", document_id=docs[2].id,
        )
        training3 = Training(
            id=generate_uuid(), tenant_id=tid, created_by=admin.id,
            title="Cell Culture Aseptic Technique",
            description="Proper BSC use, media handling, passage technique, and contamination prevention.",
            status="draft",
        )
        db.add_all([training1, training2, training3])
        db.flush()

        db.add_all([
            TrainingAssignment(
                id=generate_uuid(), training_id=training1.id,
                user_id=scientist.id, status="completed",
                completed_at=datetime(2026, 1, 15, tzinfo=timezone.utc),
                due_date=date(2026, 1, 31),
            ),
            TrainingAssignment(
                id=generate_uuid(), training_id=training1.id,
                user_id=tech.id, status="completed",
                completed_at=datetime(2026, 1, 20, tzinfo=timezone.utc),
                due_date=date(2026, 1, 31),
            ),
            TrainingAssignment(
                id=generate_uuid(), training_id=training2.id,
                user_id=scientist.id, status="completed",
                completed_at=datetime(2026, 2, 10, tzinfo=timezone.utc),
                due_date=date(2026, 2, 28),
            ),
            TrainingAssignment(
                id=generate_uuid(), training_id=training2.id,
                user_id=tech.id, status="in_progress",
                due_date=date(2026, 3, 31),
            ),
        ])

        # ── Complaints ─────────────────────────────────────────
        db.add_all([
            Complaint(
                id=generate_uuid(), tenant_id=tid, reported_by=admin.id,
                title="Customer reports precipitate in shipped buffer",
                complaint_number="COMP-0001", status="under_review",
                source="Customer email",
                product="Tris-HCl Buffer 1M pH 7.4",
                lot_number="BUF-2026-0044",
                description="Customer observed white precipitate after storing buffer at 4°C for 2 weeks.",
                investigation_notes="Likely Tris crystallization at low temperature — within normal behavior. Preparing response.",
            ),
            Complaint(
                id=generate_uuid(), tenant_id=tid, reported_by=scientist.id,
                title="Wrong item shipped — ordered 1L received 500mL",
                complaint_number="COMP-0002", status="closed",
                source="Internal",
                product="Acetonitrile HPLC Grade",
                lot_number="ACN-2026-1100",
                description="Ordered 1L bottles of acetonitrile but received 500mL. Supplier acknowledged error and reshipped.",
            ),
        ])

        db.commit()

        # Print summary
        print("=" * 60)
        print("  Discovery — Database Seeded Successfully")
        print("=" * 60)
        print()
        print(f"  Tenant:    {tenant.name} ({tenant.slug})")
        print()
        print("  Users:")
        print(f"    admin@lab.dev      / discovery  (admin)")
        print(f"    scientist@lab.dev  / discovery  (member)")
        print(f"    tech@lab.dev       / discovery  (member)")
        print()
        print("  Sample Data:")
        print(f"    Documents:          5  (+ 2 versions)")
        print(f"    Equipment:          6")
        print(f"    Calibrations:       3")
        print(f"    Suppliers:          4")
        print(f"    Risks:              4")
        print(f"    CAPAs:              3  (+ 4 actions)")
        print(f"    Non-Conformances:   3")
        print(f"    Deviations:         3")
        print(f"    Change Controls:    3")
        print(f"    Training:           3  (+ 4 assignments)")
        print(f"    Complaints:         2")
        print()
        print("  Total records: 39 + 10 child records")
        print()

    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
