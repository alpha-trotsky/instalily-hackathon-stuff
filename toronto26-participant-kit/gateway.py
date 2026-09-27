"""Build a gateway Client from whatever credentials this machine has, without ever printing the key.

Credential sources, in order:
1. The gitignored credentials file at the repo root (local machine).
2. GROUNDTRUTH_GATEWAY_URL + GROUNDTRUTH_KEY environment variables.
3. No key at all: a Claude Code cloud session whose environment stores the key as an API credential
   for the gateway host. Anthropic's agent proxy adds the Authorization header after the request
   leaves the VM, so the key never enters the session.

    python gateway.py market      # free budget read, also a connectivity check
"""
import json
import os
import sys
from pathlib import Path
from client import Client

CREDENTIALS = Path(__file__).resolve().parent.parent / 'app-141-1d2abb-credentials.json'
DEFAULT_URL = 'https://gt-gateway-wavddee32q-uc.a.run.app'
SYSTEM_CA_BUNDLE = Path('/etc/ssl/certs/ca-certificates.crt')


def _trust_cloud_proxy():
    """httpx trusts certifi by default; the cloud agent proxy's CA lives in the system store."""
    if os.environ.get('CLAUDE_CODE_REMOTE') != 'true' or os.environ.get('SSL_CERT_FILE'):
        return
    bundle = os.environ.get('REQUESTS_CA_BUNDLE') or os.environ.get('CURL_CA_BUNDLE')
    if bundle and Path(bundle).exists():
        os.environ['SSL_CERT_FILE'] = bundle
    elif SYSTEM_CA_BUNDLE.exists():
        os.environ['SSL_CERT_FILE'] = str(SYSTEM_CA_BUNDLE)


def make_client():
    if CREDENTIALS.exists():
        credentials = json.loads(CREDENTIALS.read_text())
        return Client(credentials['gateway_url'], credentials['gateway_key'])
    _trust_cloud_proxy()
    url = os.environ.get('GROUNDTRUTH_GATEWAY_URL', DEFAULT_URL)
    return Client(url, os.environ.get('GROUNDTRUTH_KEY') or None)


if __name__ == '__main__':
    with make_client() as client:
        for system in sys.argv[1:] or ['market']:
            print(system, client.budget(system))
