"""Seed development data when the database is empty."""

from datetime import date, timedelta

from sqlalchemy import func, select

from app.database import async_session
from app.models.borrower import Borrower, Loan, LoanStatus
from app.models.policy_chunk import PolicyChunk
from app.models.user import User
from app.utils.auth import get_password_hash

SAMPLE_POLICY = """
§1.1 – Purpose
This credit policy governs all lending activities of the institution.

§2.1 – Maximum LTV Ratio
The maximum loan-to-value (LTV) ratio for commercial loans is 70%.
For residential mortgages, the maximum LTV is 80%.

§3.1 – Grace Period
Borrowers are granted a grace period of 5 business days for late payments
before penalty interest is applied.

§3.2 – Penalty Interest
Penalty interest of 2% per month applies after the grace period expires.

§4.1 – Credit Score Requirements
Unsecured personal loans require a minimum credit score of 650.
SME loans require a minimum score of 600 with collateral.

§4.2 – Collateral Requirements
Accepted collateral for SME loans includes:
- Commercial property
- Equipment and machinery
- Bank guarantees
- Government securities

§5.1 – Credit Committee Escalation
Loans exceeding PKR 5,000,000 must be escalated to the credit committee.
Any loan with DSCR below 1.2 requires committee approval.

§6.1 – Restructuring Conditions
Loan restructuring is permitted when:
- Borrower has demonstrated payment history for at least 12 months
- Restructuring does not exceed 2 times per loan lifecycle
- New terms are approved by credit committee
"""


async def seed_if_empty():
    async with async_session() as db:
        user_count = await db.execute(select(User).limit(1))
        if user_count.scalar_one_or_none():
            return

        admin = User(
            email="admin@bank.pk",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            role="admin",
        )
        analyst = User(
            email="analyst@bank.pk",
            hashed_password=get_password_hash("analyst123"),
            full_name="Kashif Ahmed",
            role="analyst",
        )
        db.add_all([admin, analyst])

        borrowers_data = [
            ("Ayesha Khan", "+923001234567", "ayesha@example.com", "3520112345671"),
            ("Rizwan Mahmood", "+923009876543", None, "3520198765432"),
            ("Sara Farooq", "+923451234567", "sara@example.com", "3520154321987"),
            ("Usman Baig", "+923211234567", None, "3520167891234"),
            ("Nadia Tariq", "+923331234567", "nadia@example.com", "3520176543210"),
        ]
        borrowers = []
        for name, phone, email, cnic in borrowers_data:
            b = Borrower(name=name, phone=phone, email=email, cnic=cnic)
            db.add(b)
            borrowers.append(b)
        await db.flush()

        today = date.today()
        loans_data = [
            ("CR-0412", 0, 250000, 25000, today, LoanStatus.ACTIVE, 0),
            ("CR-0389", 1, 400000, 40000, today - timedelta(days=3), LoanStatus.OVERDUE, 3),
            ("CR-0451", 2, 150000, 15000, today, LoanStatus.ACTIVE, 0),
            ("CR-0301", 3, 600000, 60000, today + timedelta(days=2), LoanStatus.ACTIVE, 0),
            ("CR-0467", 4, 185000, 18500, today + timedelta(days=3), LoanStatus.ACTIVE, 0),
        ]
        for loan_num, b_idx, principal, installment, due, status, overdue in loans_data:
            db.add(
                Loan(
                    loan_number=loan_num,
                    borrower_id=borrowers[b_idx].id,
                    principal=principal,
                    installment_amount=installment,
                    next_due_date=due,
                    status=status,
                    days_overdue=overdue,
                )
            )

        chunks = [SAMPLE_POLICY[i : i + 800] for i in range(0, len(SAMPLE_POLICY), 750)]
        for i, chunk in enumerate(chunks):
            db.add(
                PolicyChunk(
                    content=chunk.strip(),
                    chunk_index=i,
                    section_title=chunk.split("\n")[1].strip() if "\n" in chunk else None,
                    embedding=None,
                )
            )

        await db.commit()
        logger_msg = "Database seeded with demo users, borrowers, loans, and policy chunks"
        print(logger_msg)
