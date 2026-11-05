from __future__ import annotations

import sys

from sqlalchemy import select

from .config import settings
from .db import SessionLocal, init_db
from .disease_packs import get_pack
from .models import Membership, Organization, Project, Run, Sample, User
from .security import hash_password
from .services.pipeline import execute_run


def _demo_user(db) -> User | None:
    return db.scalar(select(User).where(User.email == settings.demo_email))


def ensure_seed() -> None:
    init_db()
    db = SessionLocal()
    try:
        if _demo_user(db) is not None:
            return

        org = Organization(name="Topiome Demo Lab", slug="topiome-demo", plan="academic")
        user = User(
            email=settings.demo_email,
            name="Demo Researcher",
            password_hash=hash_password(settings.demo_password),
        )
        db.add_all([org, user])
        db.flush()
        db.add(Membership(user_id=user.id, org_id=org.id, role="owner"))

        breast = get_pack("breast")

        project = Project(
            org_id=org.id,
            name="Breast cancer pilot",
            description=(
                "Demo project showing a full spatial atlas workflow on synthetic data. "
                "Replace with a Visium sample to run the real baseline."
            ),
            disease_pack="breast",
            created_by=user.id,
        )
        project2 = Project(
            org_id=org.id,
            name="Colorectal validation cohort",
            description="Second demo project, ready for a new sample and run.",
            disease_pack="colorectal",
            created_by=user.id,
        )
        db.add_all([project, project2])
        db.flush()

        sample = Sample(
            org_id=org.id,
            project_id=project.id,
            name="DEMO-BRCA-01",
            external_id="DEMO-BRCA-01",
            disease_pack="breast",
            platform="visium",
            species="human",
            condition="tumor",
            sample_metadata={
                "sample_id": "DEMO-BRCA-01",
                "disease_pack": "breast",
                "platform": "visium",
                "synthetic": True,
                "note": "Synthetic demo data for product testing.",
            },
            status="demo",
        )
        sample2 = Sample(
            org_id=org.id,
            project_id=project2.id,
            name="DEMO-CRC-01",
            external_id="DEMO-CRC-01",
            disease_pack="colorectal",
            platform="visium",
            species="human",
            condition="tumor",
            sample_metadata={
                "sample_id": "DEMO-CRC-01",
                "disease_pack": "colorectal",
                "platform": "visium",
                "synthetic": True,
            },
            status="demo",
        )
        db.add_all([sample, sample2])
        db.flush()

        run = Run(
            org_id=org.id,
            project_id=project.id,
            sample_id=sample.id,
            disease_pack="breast",
            pack_version=breast["version"],
            status="queued",
            stage="queued",
            progress=0.0,
            params={"n_spots": 1200, "seed": 42},
            created_by=user.id,
        )
        db.add(run)
        db.commit()
        run_id = run.id
        db.close()

        # Execute synchronously so the demo is populated on first boot.
        execute_run(run_id)

        check = SessionLocal()
        try:
            final = check.get(Run, run_id)
            if final and final.status == "succeeded":
                print(f"✓ Demo seeded: {settings.demo_email} / {settings.demo_password}")
            else:
                print(f"! Demo run status: {final.status if final else 'missing'}")
        finally:
            check.close()
    finally:
        try:
            db.close()
        except Exception:
            pass


def main() -> int:
    ensure_seed()
    return 0


if __name__ == "__main__":
    sys.exit(main())
