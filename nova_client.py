import os
import requests
from dotenv import load_dotenv
import json


# Load .env
load_dotenv()


# Nova API
BASE_URL = "https://www.aczen.in/nova-api/v1"

API_KEY = os.getenv("NOVA_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "NOVA_API_KEY environment variable is not configured."
    )


# HTTP session
session = requests.Session()

session.headers.update({
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
})


def nova_get(path, **params):

    response = session.get(
        BASE_URL + path,
        params=params,
        timeout=30
    )

    body = response.json()

    if not response.ok:

        error = body.get("error", {})

        raise RuntimeError(
            f"Nova API Error: "
            f"{error.get('code', 'UNKNOWN')} - "
            f"{error.get('message', 'Unknown error')}"
        )

    return body


def list_all(path, **params):

    rows = []
    offset = 0

    while True:

        page = nova_get(
            path,
            limit=200,
            offset=offset,
            **params
        )

        rows.extend(page["data"])

        if not page["pagination"]["has_more"]:
            break

        offset += 200

    return rows


if __name__ == "__main__":

    print("Connecting to Nova...")

    payments = nova_get(
        "/payments",
        limit=5
    )

    print("\nPayments response:")

    print(
        json.dumps(
            payments,
            indent=4
        )
    )
