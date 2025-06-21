from mail_utils import (
    get_unanswered_emails_this_week,
    create_draft_reply,
    tag_as_drafted,
)
from services import get_service

from openai_utils import custom_response
from docs_utils import read_document

SCOPES = ["https://mail.google.com/", "https://www.googleapis.com/auth/documents"]


services = get_service(SCOPES)
GMAIL_SERVICE = services["gmail"]
DOCS_SERVICE = services["docs"]
INSTRUCTIONS_DOCUMENT_ID = "1jGswBhUadJiH8hhFnKmUx2yuhHD26gbS3aoRQJLny1o"


def create_answer_drafts(user_id="me"):
    """
    Creates answer drafts for all messages not tagged with "drafted" and tags them as "drafted" afterward.

    Args:
        service: The Gmail API service instance.
        user_id (str): The user's email ID. Usually 'me'.

    This function fetches all emails from this week without the "drafted" tag,
    creates a draft reply for each email, and then tags them as "drafted".
    """
    # Fetch only incoming emails, excluding drafts and sent emails
    print("Scanning for emails...")
    unanswered_emails = get_unanswered_emails_this_week(
        GMAIL_SERVICE, user_id, exclude_labels=["DRAFT", "SENT"]
    )
    print(f"\nFound {len(unanswered_emails)} unanswered emails.")

    for x, email in enumerate(unanswered_emails):
        print(f"\nAnswering Email {x + 1} of {len(unanswered_emails)}")
        print("--------------------------------------------------")
        print(f'Subject: {email["subject"]}')

        instructions = read_document(DOCS_SERVICE, INSTRUCTIONS_DOCUMENT_ID)

        response = custom_response(email["body"], instructions)

        draft_created = create_draft_reply(GMAIL_SERVICE, user_id, email, response)

        if draft_created:
            # Tag the email as "drafted"
            tag_as_drafted(GMAIL_SERVICE, user_id, email["id"])

        print(f"Draft created for email with subject: {email['subject']}")


create_answer_drafts()

# r = get_unanswered_emails_this_week(service, "me")
# print(r)
