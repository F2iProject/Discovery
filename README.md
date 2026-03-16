# Discovery

**Get your lab organized.** Free, open-source documentation and quality management for research teams and early-stage companies.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

---

## What is Discovery?

Discovery is a lightweight, self-hosted platform for managing the stuff every lab deals with — documents, equipment, training, deviations, and more. No compliance jargon. No enterprise sales pitch. Just structure.

**11 modules. Zero licensing fees. Deploy in 10 minutes.**

### Modules

| Module | What it does |
|--------|-------------|
| **Documents** | Version-controlled protocols, methods, and SOPs |
| **Change Control** | Track and manage changes to processes and documents |
| **CAPAs** | Corrective and preventive action tracking |
| **Risk Register** | Identify and assess risks |
| **Training** | Track who needs to learn what — and who already has |
| **Non-Conformances** | Log when things don't go as planned |
| **Deviations** | Document departures from established procedures |
| **Equipment** | Registry of lab instruments and devices |
| **Calibration** | Track calibration schedules and results |
| **Complaints** | Customer feedback intake and tracking |
| **Suppliers** | Where you get your stuff, and who to call |

---

## Quick Start

```bash
git clone https://github.com/F2iProject/Discovery.git
cd Discovery
docker compose up -d
```

Open `http://localhost:3000` in your browser. That's it.

### Requirements

- Docker & Docker Compose
- That's it. Really.

### Stack

- **Backend:** Python / FastAPI / SQLAlchemy
- **Frontend:** React / TypeScript / Vite
- **Database:** PostgreSQL 16
- **Cache:** Redis 7

---

## Who is this for?

- **Research labs** that need to organize protocols, track equipment, and document deviations
- **Early-stage companies** getting structured before compliance becomes real
- **Core facilities** managing shared instruments and training
- **Anyone** who's tired of tracking quality in spreadsheets

Discovery is **not** compliance software. It doesn't have audit trails, electronic signatures, or validated workflows. If you need those things, check out [BioQMS](https://bioqms.io).

---

## Growing out of Discovery?

When your lab becomes a company — or when the FDA comes knocking — Discovery's data model is designed to upgrade seamlessly into **BioQMS**, a compliance-ready QMS with:

- Immutable audit trails
- Electronic signatures (21 CFR Part 11)
- AI-assisted risk analysis and regulatory tools
- Full requirements-to-validation traceability

Learn more at [bioqms.io](https://bioqms.io).

---

## Contributing

We welcome contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Apache 2.0 — use it however you want.

---

*Built by a biomedical engineer, not a SaaS bro.*

F2i Partners · Fargo, ND
