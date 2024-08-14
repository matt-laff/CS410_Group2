import os
import base64
from . import assets
from .gmail_SDK_auth import GCC
from email import message_from_string
from email.message import EmailMessage
from googleapiclient.discovery import build


class SDK_Suit:
    service = None

    def __init__(self):
        creds_path = os.path.join(os.path.dirname(__file__), "Desktop_client.json")
        auth = GCC(creds_path=creds_path)
        self.service = build(serviceName="gmail", version="v1", credentials=auth.creds)

    def messages_list(self, me, maxResult=100):
        """
        Gets a list of messages in the users (me) gmail inbox.

        :param str me: The email address for the user requesting access
        :param int maxResult: The maximum number of messages to return, default 100

        :return: dict
        """
        try:
            query = "is:unread in:inbox"
            response = (
                self.service.users()
                .messages()
                .list(userId=me, maxResults=maxResult, q=query)
                .execute()
            )
            messages = response.get("messages", [])

            return messages
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def messages_get(self, me, message_id):
        """
        Gets the detail for a message from the message id

        :param str me: The email address for the user requesting access
        :param str message_id: The message id for the message to unpack

        :return: dict
        """
        try:
            message = (
                self.service.users()
                .messages()
                .get(userId=me, id=message_id, format="raw")
                .execute()
            )

            decoded_message = base64.urlsafe_b64decode(message["raw"]).decode("utf-8")
            decoded_message_content = message_from_string(decoded_message)

            message_content = {
                "snippet": message["snippet"],
                #"labels": message["labelIds"],
                "thread_id": message["threadId"],
                "message_id": message["id"],
                "cc": decoded_message_content["Cc"],
                "sizeEstimate": message["sizeEstimate"],
                "timestamp": assets.tm_fm(message["internalDate"]),
                "month": assets.get_month(message["internalDate"]),
                "subject": decoded_message_content.get("Subject", "None"),
                "sender": assets.get_name(decoded_message_content.get("From", "None")),
            }

            return message_content
        except Exception as error:
            print(f"Exception stack trace:\n{error}")
            return None

    def create_draft(self, sender, to, subject, message_cont):
        """
        create a draft in the sender's draft inbox

        :param str sender: The sender of the message
        :param str to: The recipient of the message
        :param str message_cont: The message content to use

        :return: The draft object
        """
        message = EmailMessage()
        message.set_content(message_cont, subtype="html")
        message["To"] = to
        message["From"] = sender
        message["Subject"] = subject

        # encode message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        enc_message = {"message": {"raw": encoded_message}}

        draft = (
            self.service.users()
            .drafts()
            .create(userId=sender, body=enc_message)
            .execute()
        )
        return draft

    def send_draft(self, me, draft_id):
        """
        send a draft to the users inbox

        :param str me: The user who is sending draft
        :param str draft_id: The id of the draft to send

        :return: sent draft
        """
        try:
            sent_draft = (
                self.service.users()
                .drafts()
                .send(userId=me, body={"id": draft_id})
                .execute()
            )

            return sent_draft
        except Exception as Error:
            print(f"stacktrace:\n{error}")

    def structure_ms(self, me, messages):
        """
        structure the messages into a format readable for inbox items (dict)

        :param str me: The user requesting access to service
        :param dict messages: The dict of messages to structure

        :return: structured messages
        """
        response = dict()
        for index, message in enumerate(messages):
            message_cont = self.messages_get(me, message["id"])
            response.setdefault(message_cont["month"], list())
            response[message_cont["month"]].append(message_cont)

        return response

    def get_thread(self, me, threadId):
        thread = self.service.users().threads().get(userId=me, id=threadId).execute()

        return thread

