import logging

from twilio.rest import Client

from app.config import settings
from app.services.ai_service import generate_llm_response

logger = logging.getLogger(__name__)


def _get_twilio_client() -> Client | None:
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        return None
    return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


async def send_whatsapp_reminder(to_phone: str, message: str) -> dict:
    client = _get_twilio_client()
    if client is None:
        logger.warning("Twilio not configured — simulating send to %s", to_phone)
        return {"status": "sent", "sid": "SIMULATED_SID", "simulated": True}

    to = to_phone if to_phone.startswith("whatsapp:") else f"whatsapp:{to_phone}"
    try:
        msg = client.messages.create(
            from_=settings.TWILIO_FROM_NUMBER,
            to=to,
            body=message,
        )
        logger.info("Reminder sent to %s: SID %s", to_phone, msg.sid)
        return {"status": "sent", "sid": msg.sid}
    except Exception as e:
        logger.error("Failed to send to %s: %s", to_phone, e)
        return {"status": "failed", "error": str(e)}


async def generate_reminder_message(
    borrower_name: str,
    amount: str,
    loan_number: str,
    due_status: str,
) -> str:
    prompt = f"""Write a professional, friendly payment reminder SMS in Urdu-English (Roman Urdu mixed with English) for:
- Borrower: {borrower_name}
- Amount due: {amount}
- Loan number: {loan_number}
- Status: {due_status}

Requirements:
- Max 60 words
- Polite but firm tone
- Include loan number for reference
- Sign off as "Credit Team"
- No harsh language
- If overdue: add urgency without threats"""

    try:
        return await generate_llm_response(
            system_prompt="You write concise bilingual payment reminder SMS messages.",
            user_content=prompt,
            max_tokens=300,
        )
    except RuntimeError:
        status_note = "overdue" if "overdue" in due_status.lower() else "due soon"
        return (
            f"Assalam-o-Alaikum {borrower_name}, aap ka loan {loan_number} ka "
            f"installment PKR {amount} {status_note} hai. Please jald payment karein. "
            f"Shukriya — Credit Team"
        )
