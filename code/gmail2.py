from mail_utils import (
    get_service,
    get_unanswered_emails_this_week,
    create_draft_reply,
    tag_as_drafted,
)
from openai_utils import categorize_mail, custom_response
import json

def get_correct_reply(category_number):
    # Load the responses from the JSON file
    with open("responses.json", "r", encoding="utf-8") as file:
        responses = json.load(file)

    # Fetch the response for the given category number
    reply_content = responses[str(category_number)]["response"]
    category_name = responses[str(category_number)]["category"]
    return [reply_content, category_name]

SCOPES = ["https://mail.google.com/"]


service = get_service(SCOPES)


def create_answer_drafts(service, user_id="me"):
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
        service, user_id, exclude_labels=["DRAFT", "SENT"]
    )
    print(f"\nFound {len(unanswered_emails)} unanswered emails.")

    for x, email in enumerate(unanswered_emails):
        print(f"\nAnswering Email {x + 1} of {len(unanswered_emails)}")
        print("--------------------------------------------------")
        print(f'Subject: {email["subject"]}')
        # Prepare the reply content
        content = f"{email['body']} answer"

        # Create a draft reply
        original_email = {
            "address": email["address"],
            "subject": email["subject"],
            "id": email["id"],
            "threadId": email.get(
                "threadId", None
            ),  # Ensure threadId is included if available
        }
        category_number = categorize_mail(content)

        if(category_number == 11):
            reply_content = custom_response(content)
            print("No default answer category detected, creating a custom response...")
        else:
            [reply_content, category_name] = get_correct_reply(category_number)
            print("Category:", category_number, ":", category_name)


        draft_created = create_draft_reply(
            service, user_id, original_email, reply_content
        )

        if draft_created:
            # Tag the email as "drafted"
            tag_as_drafted(service, user_id, email["id"])

        print(
            f"Draft created for email with subject: {email['subject']}"
        )


create_answer_drafts(service)

# r = get_unanswered_emails_this_week(service, "me")
# print(r)
