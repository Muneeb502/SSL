# # backend/checker.py
# import socket
# import ssl
# from datetime import datetime
# import OpenSSL.crypto

# def check_ssl(domain, port=443, timeout=5):
#     try:
#         sock = socket.create_connection((domain, port), timeout=timeout)
#         ctx = ssl._create_unverified_context()
#         with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
#             der_cert = ssock.getpeercert(binary_form=True)
#         x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, der_cert)
#         not_after = x509.get_notAfter().decode('ascii')
#         expiry = datetime.strptime(not_after, '%Y%m%d%H%M%SZ')
#         now = datetime.utcnow()
#         days_left = (expiry - now).days

#         status = "Valid" if days_left >= 0 else "Expired"
#         if 0 <= days_left < 30:
#             status = f"Expires in {days_left}d"

#         return {
#             "domain": domain,
#             "status": status,
#             "expires": expiry.strftime("%b %d, %Y"),
#             "days_remaining": days_left,
#             "last_checked": datetime.now().strftime("%b %d, %Y"),
#             "actions": "Renew" if days_left < 30 else "None"
#         }
#     except Exception as e:
#         return {
#             "domain": domain,
#             "status": "DOWN",
#             "expires": "N/A",
#             "days_remaining": 0,
#             "last_checked": datetime.now().strftime("%b %d, %Y"),
#             "actions": "Check"
#         }


"""
WITH FULL LOGS
"""


# backend/checker.py
import socket
import ssl
from datetime import datetime
import OpenSSL.crypto
import logging

log = logging.getLogger("SSL-MONITOR")

def check_ssl(domain, port=443, timeout=5):
    log.info(f"Starting SSL check for: {domain}")
    try:
        # TCP connect
        log.info(f"Connecting to {domain}:{port}")
        sock = socket.create_connection((domain, port), timeout=timeout)
        ctx = ssl._create_unverified_context()
        log.info(f"SSL handshake with {domain}")
        with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
            der_cert = ssock.getpeercert(binary_form=True)

        # Parse cert
        log.info(f"Parsing certificate for {domain}")
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, der_cert)
        not_after = x509.get_notAfter().decode('ascii')
        expiry = datetime.strptime(not_after, '%Y%m%d%H%M%SZ')
        now = datetime.utcnow()
        days_left = (expiry - now).days

        # Status logic
        if days_left < 0:
            status = "Expired"
        elif days_left < 30:
            status = f"Expires in {days_left}d"
        else:
            status = "Valid"

        log.info(f"SSL OK: {domain} → {status} (expires {expiry.strftime('%b %d, %Y')})")

        return {
            "domain": domain,
            "status": status,
            "expires": expiry.strftime("%b %d, %Y"),
            "days_remaining": days_left,
            "last_checked": datetime.now().strftime("%b %d, %Y"),
            "actions": "Renew" if days_left < 30 else "None"
        }

    except Exception as e:
        log.error(f"SSL CHECK FAILED for {domain}: {str(e)}")
        return {
            "domain": domain,
            "status": "DOWN",
            "expires": "N/A",
            "days_remaining": 0,
            "last_checked": datetime.now().strftime("%b %d, %Y"),
            "actions": "Check"
        }