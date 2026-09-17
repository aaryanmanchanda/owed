"""Phase 1 throwaway Bedrock smoke test (D-05/D-06/D-07/D-09).

NOT the production extraction path — Phase 3 builds the real extraction
Lambda at src/extract/. This module exists only to prove, one day early,
that the single riskiest technical path in this project works: a Lambda
reads image bytes out of S3 with s3.get_object and passes them straight
into a Bedrock Converse call. Step Functions' direct-Bedrock-image
integration is never used anywhere in this project (HANDOFF §9).

Per D-07 the pass bar is a schema-valid response only — no UTR regex, no
amount-positivity check, no accuracy comparison. That validation belongs to
the production extraction module in src/extract/ (Phase 3). Phase 3 may
delete this file outright once Phase 1 closes.
"""

import json
import os

import boto3

s3 = boto3.client("s3")
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

EXTRACTION_PROMPT = (
    "Extract fields from this UPI payment screenshot. "
    "Return ONLY JSON matching this schema, with no markdown fence and no "
    "extra commentary: "
    '{"utr": "string of exactly 12 digits, or null", '
    '"amount_inr": "number, or null", '
    '"screen_time": "ISO-8601 in IST, or null", '
    '"payment_app": "gpay | phonepe | paytm | bhim | other | null", '
    '"status_text": "success | pending | failed | null", '
    '"payee_name": "string or null", '
    '"notes": "short free text on legibility"}. '
    "Return null whenever you are not sure — a null is a normal result, "
    "not an error."
)


def _bedrock_image_format(key: str) -> str:
    """Derive the Bedrock image `format` from an S3 key's extension."""
    ext = key.rsplit(".", 1)[-1].lower()
    if ext == "jpg":
        return "jpeg"
    return ext


def lambda_handler(event, context):
    try:
        bucket = event.get("bucket") or os.environ["SMOKE_BUCKET"]
        key = event["key"]

        obj = s3.get_object(Bucket=bucket, Key=key)
        image_bytes = obj["Body"].read()
        image_format = _bedrock_image_format(key)

        message = {
            "role": "user",
            "content": [
                {"text": EXTRACTION_PROMPT},
                {
                    "image": {
                        "format": image_format,
                        # Raw bytes — boto3 performs the encoding itself.
                        # Pre-base64-encoding here produces a malformed
                        # request (RESEARCH Anti-Patterns).
                        "source": {"bytes": image_bytes},
                    }
                },
            ],
        }

        response = bedrock.converse(
            modelId=os.environ["BEDROCK_PROFILE_ID"],
            messages=[message],
        )

        output_text = response["output"]["message"]["content"][0]["text"]
        # Strip a markdown fence if the model added one despite instructions.
        cleaned = output_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()

        extracted = json.loads(cleaned)

        return {"statusCode": 200, "body": json.dumps(extracted)}

    except Exception as exc:  # noqa: BLE001 - smoke test wants a legible 500
        return {"statusCode": 500, "body": str(exc)}
