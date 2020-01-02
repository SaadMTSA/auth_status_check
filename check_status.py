"""
This script fetches the status of a USCIS case and sends it to a designated number as an SMS
"""
import os
import urllib3
import logging
import click
from twilio.rest import Client


def get_case_status(case_number: str) -> str:
    """
    Gets status from USCIS site
    """
    urllib3.disable_warnings()
    http = urllib3.PoolManager(cert_reqs=False, assert_hostname=False)
    req = http.request(
        "POST",
        "https://egov.uscis.gov/casestatus/mycasestatus.do",
        fields={"appReceiptNum": case_number},
    )
    return _get_status(req.data)


def _get_status(data: str) -> str:
    """
    Gets status from the returned html string
    """
    my_str = data.decode("utf-8")
    idx = my_str.find("Your Current Status:")
    n_idx = my_str.find("\n", idx)
    return my_str[n_idx:].split("\n")[1].strip()


@click.command()
@click.argument("case-number")
@click.argument("msg-to")
@click.argument("msg-from")
def send_message(case_number: str, msg_to: str, msg_from: str) -> None:
    """
    Sends an sms about a USCIS case status from a twilio number to another one
    """
    client = Client(os.environ["TW_SID"], os.environ["TW_TOKEN"])
    client.messages.create(to=msg_to, from_=msg_from, body=get_case_status(case_number))
    logging.info("Message sent from %s to %s." % (msg_from, msg_to))


if __name__ == "__main__":
    send_message()
