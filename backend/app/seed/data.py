from datetime import date
from decimal import Decimal

POLICIES = [
    {
        "product_code": "A",
        "name": "HomeSafe Comprehensive",
        "coverage_text": (
            "Product A (HomeSafe Comprehensive) covers the insured dwelling and contents "
            "against fire, smoke, explosion, theft, vandalism, storm, and sudden water "
            "damage from burst pipes or overflowing appliances. Temporary accommodation "
            "is included for up to 30 days when the home is uninhabitable."
        ),
        "exclusions": (
            "Flood and storm surge are excluded unless a flood endorsement is attached. "
            "Wear and tear, gradual seepage, poor workmanship, and damage while the home "
            "is unoccupied for more than 60 consecutive days are excluded."
        ),
        "limitations": (
            "Buildings limit $500,000. Contents limit $75,000. Water-damage sublimit "
            "$25,000 per event. Excess $750. Claims must be notified within 30 days of "
            "the incident."
        ),
    },
    {
        "product_code": "B",
        "name": "DriveShield Motor",
        "coverage_text": (
            "Product B (DriveShield Motor) is comprehensive motor cover for the listed "
            "vehicle. It includes accidental collision, theft, fire, windscreen, and "
            "third-party property damage up to $20,000,000. A courtesy vehicle is "
            "available for up to 14 days after an approved claim."
        ),
        "exclusions": (
            "Driving under the influence, unlicensed drivers, racing, and using the "
            "vehicle for hire or reward are excluded. Mechanical failure and tyre "
            "damage (unless caused by a covered collision) are excluded."
        ),
        "limitations": (
            "Agreed value as shown on the schedule. Windscreen claims are limited to "
            "two per year without excess. Standard excess $600. At-fault claims may "
            "affect no-claim discount."
        ),
    },
    {
        "product_code": "C",
        "name": "VoyageCare Travel",
        "coverage_text": (
            "Product C (VoyageCare Travel) covers overseas medical expenses, trip "
            "cancellation, lost baggage, and personal liability for journeys up to "
            "45 days. Emergency evacuation and 24-hour assistance are included."
        ),
        "exclusions": (
            "Pre-existing medical conditions that were not declared, travel against "
            "medical advice, and destinations subject to a government 'do not travel' "
            "advisory are excluded. High-risk adventure sports require an endorsement."
        ),
        "limitations": (
            "Medical expenses up to $2,000,000. Cancellation up to $10,000. Baggage "
            "up to $3,000 ($500 per item). Claims for cancellation must be lodged "
            "within 14 days of the event that caused the cancellation."
        ),
    },
]

CUSTOMERS = [
    {
        "full_name": "Amelia Chen",
        "date_of_birth": date(1988, 3, 14),
        "email": "amelia.chen@example.com",
        "policy_number": "POL-A-10021",
        "product_code": "A",
        "last4_id": "4421",
    },
    {
        "full_name": "Marcus Webb",
        "date_of_birth": date(1975, 11, 2),
        "email": "marcus.webb@example.com",
        "policy_number": "POL-B-20014",
        "product_code": "B",
        "last4_id": "8810",
    },
    {
        "full_name": "Priya Nair",
        "date_of_birth": date(1992, 7, 29),
        "email": "priya.nair@example.com",
        "policy_number": "POL-C-30008",
        "product_code": "C",
        "last4_id": "1194",
    },
    {
        "full_name": "James Okafor",
        "date_of_birth": date(1984, 1, 19),
        "email": "james.okafor@example.com",
        "policy_number": "POL-A-10087",
        "product_code": "A",
        "last4_id": "6732",
    },
    {
        "full_name": "Elena Rossi",
        "date_of_birth": date(1990, 9, 5),
        "email": "elena.rossi@example.com",
        "policy_number": "POL-B-20055",
        "product_code": "B",
        "last4_id": "3058",
    },
]

# claim_number, customer policy_number, incident fields, status, summary, events
CLAIMS = [
    {
        "claim_number": "CLM-2026-0001",
        "policy_number": "POL-A-10021",
        "incident_date": date(2026, 6, 12),
        "incident_type": "water_damage",
        "description": "Burst washing-machine hose flooded the laundry and adjacent hallway.",
        "location": "14 Harbour Lane, Singapore",
        "estimated_amount": Decimal("4200.00"),
        "status": "under_review",
        "summary": "Water damage from appliance failure. Adjuster assigned, photos received.",
        "events": [
            ("submitted", "Claim lodged by operations after customer call."),
            ("under_review", "Adjuster assigned. Awaiting plumber invoice."),
        ],
    },
    {
        "claim_number": "CLM-2026-0002",
        "policy_number": "POL-B-20014",
        "incident_date": date(2026, 5, 3),
        "incident_type": "collision",
        "description": "Rear-end collision at a traffic light. Other party admitted fault.",
        "location": "Ayer Rajah Expressway, Singapore",
        "estimated_amount": Decimal("6800.00"),
        "status": "approved",
        "summary": "Third-party at fault. Repair authorised at preferred workshop.",
        "events": [
            ("submitted", "Claim lodged with police report."),
            ("under_review", "Liability confirmed from third-party insurer."),
            ("approved", "Repair authorised. Courtesy car offered."),
        ],
    },
    {
        "claim_number": "CLM-2026-0003",
        "policy_number": "POL-C-30008",
        "incident_date": date(2026, 4, 18),
        "incident_type": "lost_baggage",
        "description": "Checked bag did not arrive after flight SIN-NRT.",
        "location": "Narita Airport, Tokyo",
        "estimated_amount": Decimal("890.00"),
        "status": "paid",
        "summary": "Airline PIR provided. Baggage benefit paid at itemised value.",
        "events": [
            ("submitted", "Claim lodged with PIR and receipts."),
            ("approved", "Item limits applied."),
            ("paid", "Settlement of $890 issued."),
        ],
    },
    {
        "claim_number": "CLM-2026-0004",
        "policy_number": "POL-A-10087",
        "incident_date": date(2026, 7, 1),
        "incident_type": "theft",
        "description": "Forced entry; laptop and jewellery taken from the study.",
        "location": "88 Newton Road, Singapore",
        "estimated_amount": Decimal("5400.00"),
        "status": "information_required",
        "summary": "Police report on file. Waiting for purchase receipts for jewellery.",
        "events": [
            ("submitted", "Claim lodged with police report."),
            ("information_required", "Requested receipts and serial numbers."),
        ],
    },
    {
        "claim_number": "CLM-2026-0005",
        "policy_number": "POL-B-20055",
        "incident_date": date(2026, 3, 22),
        "incident_type": "windscreen",
        "description": "Stone chip cracked the windscreen on the PIE.",
        "location": "Pan Island Expressway, Singapore",
        "estimated_amount": Decimal("480.00"),
        "status": "paid",
        "summary": "Windscreen replacement completed. No excess applied.",
        "events": [
            ("submitted", "Windscreen claim lodged."),
            ("approved", "Replacement authorised."),
            ("paid", "Workshop paid directly."),
        ],
    },
    {
        "claim_number": "CLM-2026-0006",
        "policy_number": "POL-A-10021",
        "incident_date": date(2026, 1, 9),
        "incident_type": "storm",
        "description": "Fallen tree damaged roof tiles and a bedroom ceiling after a storm.",
        "location": "14 Harbour Lane, Singapore",
        "estimated_amount": Decimal("9100.00"),
        "status": "paid",
        "summary": "Storm damage assessed and settled after roof repair.",
        "events": [
            ("submitted", "Storm claim lodged with photos."),
            ("under_review", "Surveyor inspected the roof."),
            ("approved", "Repairs approved."),
            ("paid", "Settlement issued to contractor."),
        ],
    },
    {
        "claim_number": "CLM-2026-0007",
        "policy_number": "POL-C-30008",
        "incident_date": date(2026, 8, 2),
        "incident_type": "trip_cancellation",
        "description": "Trip cancelled after sudden hospital admission of travelling companion.",
        "location": "Singapore",
        "estimated_amount": Decimal("2100.00"),
        "status": "rejected",
        "summary": "Companion was not a covered travelling companion on the schedule.",
        "events": [
            ("submitted", "Cancellation claim lodged."),
            ("under_review", "Policy schedule reviewed."),
            ("rejected", "Companion not listed as a covered traveller."),
        ],
    },
    {
        "claim_number": "CLM-2026-0008",
        "policy_number": "POL-B-20014",
        "incident_date": date(2026, 8, 20),
        "incident_type": "theft",
        "description": "Vehicle stolen from basement car park overnight.",
        "location": "Tanjong Pagar Centre, Singapore",
        "estimated_amount": Decimal("28500.00"),
        "status": "submitted",
        "summary": "Theft claim just lodged. Police report uploaded. Investigation not started.",
        "events": [
            ("submitted", "Theft claim lodged with police report."),
        ],
    },
]
