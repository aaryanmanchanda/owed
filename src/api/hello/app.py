import json
import os


def lambda_handler(event, context):
    """Phase 1 tracer: proves API Gateway (HTTP API) -> Lambda deploys and
    answers in ap-south-1. Returning AWS_REGION in the body is what proves
    the stack landed in the locked region, not just that some Lambda answered.
    """
    body = {
        "message": "hello from owed",
        "region": os.environ.get("AWS_REGION"),
    }
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
