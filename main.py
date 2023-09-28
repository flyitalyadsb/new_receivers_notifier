import datetime
import json
import os
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from difflib import ndiff

import pytz

FROM = os.environ.get('FROM')
TO = os.environ.get('TO')
SERVER = os.environ.get('SERVER')
USER = os.environ.get('SERVER') if os.environ.get('SERVER') else FROM
PASSWORD = os.environ.get('EMAIL_PASSWORD')
TIMEZONE = os.environ.get('TIMEZONE') if os.environ.get('TIMEZONE') else 'Europe/Rome'

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
        msg['From'] = FROM
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
            server.sendmail(FROM, TO, msg.as_string())

        old_peers = lista_peer

        time.sleep(((datetime.datetime.now(pytz.timezone(TIMEZONE)).replace(hour=0, minute=0, second=0,
                                                                                 microsecond=0) + datetime.timedelta(
            days=1)) - datetime.datetime.now(pytz.timezone(TIMEZONE))).total_seconds())
