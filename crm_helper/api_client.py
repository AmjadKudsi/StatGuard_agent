import requests


def fetch_customer_record(base_url: str, customer_id: str) -> dict:
    """
    Fetch a customer record from an internal CRM API.

    This function contains multiple issues:
      * It accepts a base_url from the caller (could be untrusted).
      * It disables TLS certificate verification.
    """
    url = f"{base_url.rstrip('/')}/customers/{customer_id}"

    # DELIBERATE VULNERABILITY: verify=False and user-controlled URL.
    response = requests.get(url, timeout=5, verify=False)
    response.raise_for_status()
    return response.json()
