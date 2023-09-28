import datetime
import json
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from difflib import ndiff
import argparse
import pytz


parser = argparse.ArgumentParser(description="Sample script that accepts flags")

parser.add_argument("--from_email", default=None, help="Sender's email address")
parser.add_argument("--to", default=None, help="Receiver's email address")
parser.add_argument("--server", default=None, help="Mail server")
parser.add_argument("--user", default=None, help="Username for mail server access")
parser.add_argument("--password", default=None, help="Password for mail server access")
parser.add_argument("--timezone", default='Europe/Rome', help="Time zone")

args = parser.parse_args()

FROM_EMAIL = args.from_email
TO = args.to
SERVER = args.server
USER = args.user if args.user else args.from_email
PASSWORD = args.password
TIMEZONE = args.timezone

old_peers = {}

while True:
    # Read from clients.json
    with open("/data/clients.json", "r") as file:
        data = json.load(file)

    lista_peer = [str(token.split('_')[0]) for token in data.keys()]
    lista_peer.sort()
    if lista_peer != old_peers:
        different_peers = list(ndiff(lista_peer, old_peers))
        different_peers_str = json.dumps(different_peers)

        # Setting up email
        msg = MIMEMultipart('alternative')
        msg['From'] = FROM_EMAIL
        msg['To'] = TO
        msg['Subject'] = f'Users Update - Aggiornamento Utenti {datetime.datetime.now().strftime("%d-%m-%y")}'

        # HTML for the email
        html = f"""<div>
        <h1>Users Update - Aggiornamento Utenti</h1>
        <pre>{different_peers_str}</pre>
        </div>
        <style>div {{margin-left: auto; margin-right: auto;}} h1{{font-family: Helvetica;}}</style>
        """
        msg.attach(MIMEText(html, 'html'))

        # Send email using SMTP
        with smtplib.SMTP_SSL(SERVER, 465) as server:
            server.login(USER, PASSWORD)
            server.sendmail(FROM_EMAIL, TO, msg.as_string())

        old_peers = lista_peer
        print("Email sent!")
        time.sleep(((datetime.datetime.now(pytz.timezone(TIMEZONE)).replace(hour=0, minute=0, second=0,
                                                                                 microsecond=0) + datetime.timedelta(
            days=1)) - datetime.datetime.now(pytz.timezone(TIMEZONE))).total_seconds())
    print("Email not sent: same peers of yesterday.")
