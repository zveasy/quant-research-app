"""Lambda triggered by Persona webhook to activate accounts."""

from __future__ import annotations

import json
import os

import boto3
import boto3.session

DDB_TABLE = os.environ.get("DDB_TABLE", "kyc-users")
SES_EMAIL = os.environ.get("SES_EMAIL", "compliance@example.com")

db = boto3.resource("dynamodb").Table(DDB_TABLE)
ses = boto3.client("ses")


def lambda_handler(event, context):
    record = json.loads(event.get("body", "{}"))
    status = record.get("status")
    sanctions = record.get("sanctions")
    user_id = record.get("reference_id")

    if status == "passed" and sanctions == "clear":
        db.put_item(Item={"user_id": user_id, "status": "active"})
    else:
        ses.send_email(
            Source=SES_EMAIL,
            Destination={"ToAddresses": [SES_EMAIL]},
            Message={
                "Subject": {"Data": "KYC Failed"},
                "Body": {"Text": {"Data": json.dumps(record)}},
            },
        )
    return {"statusCode": 200}
