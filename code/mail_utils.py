import base64
import re
from email.mime.text import MIMEText
from datetime import datetime, timedelta


def get_unread_emails(service, user_id="me"):
    """
    Checks the mailbox for unread messages

    args:
        service: see get_service()
        user_id: should ALWAYS be "me"

    return:
        list of dictionaries with the following structure:
        [
            {
            'id': (str),
            'name': (str),
            'address': (str),
            'subject': (str),
            'body': (str)
            }
        ]
    """
    try:
        response = (
            service.users().messages().list(userId=user_id, q="is:unread").execute()
        )
        messages = response.get("messages", [])
        emails = []

        for message in messages:
            msg_id = message["id"]
            msg = (
                service.users()
                .messages()
                .get(userId=user_id, id=msg_id, format="full")
                .execute()
            )

            # Extract the sender's email address and name using regex
            sender_info = next(
                header["value"]
                for header in msg["payload"]["headers"]
                if header["name"] == "From"
            )
            email_match = re.search(r"<(.+?)>", sender_info)
            sender_email = email_match.group(1) if email_match else sender_info
            sender_name = re.search(r"(.+?) <", sender_info)
            sender_name = sender_name.group(1) if sender_name else ""

            # Extract the subject
            subject = next(
                header["value"]
                for header in msg["payload"]["headers"]
                if header["name"] == "Subject"
            )

            # Extract the message body
            parts = msg["payload"].get("parts", [])
            body = ""
            for part in parts:
                if part["mimeType"] == "text/plain":
                    body_data = part["body"]["data"]
                    body = base64.urlsafe_b64decode(body_data).decode("utf-8")
                    break

            email_info = {
                "id": msg_id,
                "name": sender_name,
                "address": sender_email,
                "subject": subject,
                "body": body,
            }
            emails.append(email_info)

        return emails
    except Exception as error:
        print(f"An error occurred: {error}")
        return []


def get_unanswered_emails_this_week(service, user_id="me", exclude_labels=None):
    """
    Fetches unanswered emails from this week, excluding drafts and sent emails.

    Args:
        service: The Gmail API service instance.
        user_id (str): The user's email ID. Usually 'me'.
        exclude_labels (list): List of labels to exclude (e.g., ["DRAFT", "SENT"]).

    Returns:
        list: A list of emails matching the criteria.
    """
    # Calculate the start of the week (Monday)
    start_of_week = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y/%m/%d')

    # Build the query to exclude drafts and sent emails
    query = f"after:{start_of_week} -label:DRAFTED label:INBOX"

    response = service.users().messages().list(userId=user_id, q=query).execute()
    messages = response.get("messages", [])
    emails = []

    for message in messages:
        msg_id = message["id"]
        msg = (
            service.users()
            .messages()
            .get(userId=user_id, id=msg_id, format="full")
            .execute()
        )

        # Extract the sender's email address and name using regex
        sender_info = next(
            header["value"]
            for header in msg["payload"]["headers"]
            if header["name"] == "From"
        )
        email_match = re.search(r"<(.+?)>", sender_info)
        sender_email = email_match.group(1) if email_match else sender_info
        sender_name = re.search(r"(.+?) <", sender_info)
        sender_name = sender_name.group(1) if sender_name else ""

        # Extract the subject
        try:
            subject = next(
                header["value"]
                for header in msg["payload"]["headers"]
                if header["name"].lower() == "subject"
            )
        except StopIteration:
            subject = "No Subject"  # Default value if no subject is found

        # Extract the message body
        parts = msg["payload"].get("parts", [])
        body = ""
        for part in parts:
            if part["mimeType"] == "text/plain":
                body_data = part["body"]["data"]
                body = base64.urlsafe_b64decode(body_data).decode("utf-8")
                break

        message_id = next(
            (
                header["value"]
                for header in msg["payload"]["headers"]
                if header["name"].lower() == "message-id"
            ),
            None,
        )

        email_info = {
            "id": msg_id,
            "threadId": msg.get("threadId"),
            "messageId": message_id,
            "name": sender_name,
            "address": sender_email,
            "subject": subject,
            "body": body,
            "labels": msg.get("labelIds", []),  # Include labels in email info
        }
        emails.append(email_info)

    return emails


def mark_as_read(service, user_id, msg_id):
    """
    Marks a specified email as read.

    Args:
        service: The Gmail API service instance.
        user_id (str): The user's email ID. Usually 'me'.
        msg_id (str): The unique ID of the email to be marked as read.
    return:
        True if successfully marked as read else false
    """

    try:
        service.users().messages().modify(
            userId=user_id, id=msg_id, body={"removeLabelIds": ["UNREAD"]}
        ).execute()
        print(f"Marked message {msg_id} as read.")
        return True
    except Exception as error:
        print(f"An error occurred: {error}")
        return False


def ensure_label_exists(service, user_id, label_name):
    """
    Ensures that a label exists in the user's Gmail account. If it doesn't exist, creates it.

    Args:
        service: The Gmail API service instance.
        user_id (str): The user's email ID. Usually 'me'.
        label_name (str): The name of the label to ensure.

    Returns:
        str: The ID of the label.
    """
    try:
        # Get the list of existing labels
        labels = service.users().labels().list(userId=user_id).execute().get("labels", [])
        for label in labels:
            if label["name"] == label_name:
                return label["id"]

        # Create the label if it doesn't exist
        label_body = {
            "name": label_name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
        }
        new_label = service.users().labels().create(userId=user_id, body=label_body).execute()
        print(f"Created label: {label_name}")
        return new_label["id"]
    except Exception as error:
        print(f"An error occurred ensuring the label exists: {error}")
        return None


def tag_as_drafted(service, user_id, msg_id):
    """
    Tags a specified email with the "drafted" label.

    Args:
        service: The Gmail API service instance.
        user_id (str): The user's email ID. Usually 'me'.
        msg_id (str): The unique ID of the email to be tagged.

    Returns:
        bool: True if successfully tagged, False otherwise.
    """
    try:
        # Ensure the "DRAFTED" label exists
        label_id = ensure_label_exists(service, user_id, "DRAFTED")
        if not label_id:
            return False

        # Add the label to the message
        service.users().messages().modify(
            userId=user_id, id=msg_id, body={"addLabelIds": [label_id]}
        ).execute()
        # print(f"Tagged message {msg_id} as drafted.")
        return True
    except Exception as error:
        print(f"An error occurred tagging the message: {error}")
        return False

def create_message(sender, to, subject, message_text):
    """
    Creates a message

    params:

    sender (str): The e-mail adress of the sender
    to (str): The e-mail adress of the receiver
    subject (str): The subject of the mail
    message_text (str): The message text

    return: A raw encoded message ready to be sent using send_message()
    """
    message = MIMEText(message_text)
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    return {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}


def send_message(service, user_id, message):
    """
    Sends an email message.

    Args:
        service: The Gmail API service instance.
        user_id (str): The user's email ID. Usually 'me'.
        message (dict): The message to be sent. Should be created using create_message.

    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """
    try:
        message = (
            service.users().messages().send(userId=user_id, body=message).execute()
        )
        print(f"Sent {message['id']} successfully")
        return True
    except Exception as error:
        print(f"An error occurred sending the message: {error}")
        return False


def create_draft(service, user_id, message):
    """
    Creates a draft email.

    Args:
        service: The Gmail API service instance.
        user_id (str): The user's email ID. Usually 'me'.
        message (dict): The message to be saved as a draft. Should be created using create_message.

    Returns:
        bool: True if the draft was created successfully, False otherwise.
    """
    try:
        draft = service.users().drafts().create(userId=user_id, body={"message": message}).execute()
        return True
    except Exception as error:
        print(f"An error occurred creating the draft: {error}")
        return False


def create_draft_reply(service, user_id, original_email, reply_content):
    """
    Creates a draft reply to an existing email in the same thread.

    Args:
        service: The Gmail API service instance.
        user_id (str): The user's email ID. Usually 'me'.
        original_email (dict): The original email to reply to. Should contain 'address', 'subject', 'id', and 'threadId'.
        reply_content (str): The content of the reply.

    Returns:
        bool: True if the draft was created successfully, False otherwise.
    """
    try:
        reply_subject = f"Re: {original_email['subject']}"
        message = MIMEText(reply_content)
        message["to"] = original_email["address"]
        message["from"] = user_id
        message["subject"] = reply_subject
        message["In-Reply-To"] = original_email["messageId"]
        message["References"] = original_email["messageId"]

        raw_message = {
            "raw": base64.urlsafe_b64encode(message.as_bytes()).decode(),
            "threadId": original_email["threadId"],
        }
        return create_draft(service, user_id, raw_message)
    except Exception as error:
        print(f"An error occurred creating the draft reply: {error}")
        return False


def respond_to_mails(service, sender_adress, user_id):
    """
    Responds to unread emails with a specific subject.

    Args:
        service: The Gmail API service instance.
        sender_address (str): The email address of the sender (response sender).
        user_id (str): The user's email ID. Usually 'me'.

    This function scans for unread emails with the subject 'info',
    creates a response, sends it, and marks the original email as read.
    """
    unread_emails = get_unread_emails(service)

    for email in unread_emails[0:5]:
        if email["subject"].lower() == "info":

            response_text = f'Hej {email["name"]}. Det här är ska senare vara svaret till frågan: {email["body"]}'

            message = create_message(
                sender=sender_adress,
                to=email["address"],
                subject=f'Svar till frågan {email["body"][:50]}',
                message_text=response_text,
            )

            send_message(service, user_id, message)
            mark_as_read(service, user_id, email["id"])
