"""Plain-language financial literacy modules for self-employed users."""

LITERACY_MODULES = [
    {
        "id": "architect-not-engine",
        "title": "You Are the Architect, Not the Engine",
        "order": 1,
        "summary": "Your job is to design systems. The machine runs even when you are tired.",
        "body": (
            "Self-employed people often trade hours for money. That works until you cannot work. "
            "An **architect** builds a **machine**: rules for every dollar, a cushion for emergencies, "
            "and assets that pay you back. This app automates the boring parts so you stay the designer—not the worker."
        ),
        "key_point": "If your money depends on your presence, your freedom is temporary.",
    },
    {
        "id": "156520",
        "title": "The 15/65/20 Rule",
        "order": 2,
        "summary": "Split every dollar before it arrives—Future, Essentials, Life.",
        "body": (
            "**15% Future** — Stability Fund, paying off bad debt, investments.\n\n"
            "**65% Essentials** — Non-negotiable costs to live and run your business.\n\n"
            "**20% Life** — Discretionary spending. Use the 72-hour pause before non-essential buys.\n\n"
            "When Essentials creep above 65% of income, you are structurally fragile—fix that before chasing opportunities."
        ),
        "key_point": "Assign a job to every dollar before it arrives.",
    },
    {
        "id": "stability-fund",
        "title": "Stability Fund (3–6 Months)",
        "order": 3,
        "summary": "Your shock absorber—not an investment account.",
        "body": (
            "Calculate one month of **Essentials** (not total spending). Multiply by 3–6 months. "
            "That is your target. Fund it from the **Future** bucket (15%) until full.\n\n"
            "This fund is why you can say no to bad clients, take a sick day, or invest without panic. "
            "No Stability Fund = no sovereignty."
        ),
        "key_point": "Retention before earning. Cushion before leverage.",
    },
    {
        "id": "stages",
        "title": "The Wealth Stages",
        "order": 4,
        "summary": "Stability → Skill Stacking → Assets → Sovereignty. No skipping.",
        "body": (
            "1. **Stability** — Fund the cushion; run 15/65/20 mechanically.\n"
            "2. **Skill Stacking** — Earn more per hour; stack skills that multiply income.\n"
            "3. **Asset Acquisition** — Productize knowledge or buy cash-flowing assets.\n"
            "4. **Sovereignty** — Passive income covers essentials; freedom from volatility.\n\n"
            "Advanced tools (opportunity flipping, etc.) unlock later—they are not the starting line."
        ),
        "key_point": "Systems over motivation. The app enforces the sequence.",
    },
    {
        "id": "self-trust",
        "title": "Self-Trust and Integrity",
        "order": 5,
        "summary": "External trust starts with keeping promises to yourself.",
        "body": (
            "Your **Integrity Score** tracks follow-through: pause rule honored, commitments kept, "
            "steady habits over hype. This is for **you**—not a credit bureau score.\n\n"
            "Quiet consistency beats loud bursts. Banks and partners trust people who do what they say—"
            "starting with what you say to yourself."
        ),
        "key_point": "Ordinary actions repeated consistently build real leverage.",
    },
    {
        "id": "consumer-operator",
        "title": "Consumer vs Operator Mindset",
        "order": 6,
        "summary": "Operators see gaps; consumers react to trends.",
        "body": (
            "**Consumer** spend: status, boredom, keeping up appearances.\n"
            "**Operator** spend: tools, skills, assets that return value.\n\n"
            "The app flags invisible emotional spending so you can pause and choose. "
            "You are training operator awareness—not deprivation."
        ),
        "key_point": "Complaints are signals. Inefficiency is inventory.",
    },
    {
        "id": "credit-utilization",
        "title": "Credit Utilization — The Fast Lever",
        "order": 7,
        "summary": "Keep revolving utilization under 30% — ideally under 10% before applying for loans.",
        "body": (
            "Credit scores heavily weight **how much of your limit you use**. "
            "Pay down highest-utilization cards first—even before the lowest balance.\n\n"
            "Request limit increases only after 6+ on-time months; don't spend into the new limit."
        ),
        "key_point": "Utilization is a speedometer — pay before statement close when possible.",
    },
    {
        "id": "credit-disputes",
        "title": "Cleaning Your Credit Report",
        "order": 8,
        "summary": "Dispute inaccurate items; negotiate pay-for-delete on valid collections.",
        "body": (
            "Pull free reports from AnnualCreditReport.com. Dispute **inaccurate** items in writing with bureaus.\n\n"
            "For valid collections, negotiate **pay-for-delete** in writing before paying. "
            "Keep records. This is educational guidance—not legal advice."
        ),
        "key_point": "Accuracy first. Never dispute accurate debts hoping they vanish.",
    },
    {
        "id": "loan-readiness",
        "title": "Loan Readiness (DTI & Documentation)",
        "order": 9,
        "summary": "Lenders want stable income, low DTI, and clean payment history.",
        "body": (
            "**Debt-to-income (DTI)** = monthly debt payments ÷ gross monthly income. "
            "Many lenders prefer DTI under 43% for business credit.\n\n"
            "Prepare: 2 years tax returns, bank statements, profit & loss, and a written use-of-funds for acquisition debt only."
        ),
        "key_point": "Acquisition debt for assets that cash-flow — never ego consumption.",
    },
]


def get_modules() -> list[dict]:
    return sorted(LITERACY_MODULES, key=lambda m: m["order"])


def get_module(module_id: str) -> dict | None:
    for m in LITERACY_MODULES:
        if m["id"] == module_id:
            return m
    return None
