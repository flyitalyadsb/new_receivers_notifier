import datetime
import json
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import argparse
import pytz

parser = argparse.ArgumentParser(description="Sample script that accepts flags")

parser.add_argument("--from_email", default=None, help="Sender's email address")
parser.add_argument("--to", default=None, help="Receiver's email address")
parser.add_argument("--server", default=None, help="Mail server")
parser.add_argument("--port", default=465, help="Port server")
parser.add_argument("--user", default=None, help="Username for mail server access")
parser.add_argument("--password", default=None, help="Password for mail server access")
parser.add_argument("--timezone", default='Europe/Rome', help="Time zone")

args = parser.parse_args()

FROM_EMAIL = args.from_email
TO = args.to
SERVER = args.server
PORT = args.port
USER = args.user if args.user else args.from_email
PASSWORD = args.password
TIMEZONE = args.timezone

old_peers = {}

while True:
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    # Read from clients.json
    with open("/data/clients.json", "r") as file:
        data = json.load(file)

    lista_peer = [str(token.split('_')[0]) for token in data.keys()]
    lista_peer.sort()

    if lista_peer != old_peers:
        lista_peer_set = set(lista_peer)
        old_peers_set = set(old_peers)

        added_peers = lista_peer_set - old_peers_set
        removed_peers = old_peers_set - lista_peer_set

        added_dict = {index: value for index, value in enumerate(added_peers)}
        removed_dict = {index: value for index, value in enumerate(removed_peers)}

        result = [added_dict, removed_dict]

        different_peers_str = json.dumps(result)

        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = TO
        msg['Subject'] = f'Users Update - Aggiornamento Utenti {datetime.datetime.now().strftime("%d-%m-%y")}'
        html_output = f"""
        <div style="color: white; font-size: 1px; max-height: 0; overflow: hidden;">
        {result}
        </div>
        """
        html_output += "<table border='1'>"
        html_output += "<thead><tr><th>Index</th><th>New</th><th>Removed</th></tr></thead>"
        html_output += "<tbody>"
        for i in range(max(len(added_dict), len(removed_dict))):
            html_output += "<tr>"

            # Indice
            html_output += f"<td>{i}</td>"

            # Aggiunto
            if i in added_dict:
                html_output += f"<td>{added_dict[i]}</td>"
            else:
                html_output += "<td></td>"

            # Rimosso
            if i in removed_dict:
                html_output += f"<td>{removed_dict[i]}</td>"
            else:
                html_output += "<td></td>"

            html_output += "</tr>"

        html_output += "</tbody>"
        html_output += "</table>"

        msg.attach(MIMEText(html_output, 'html'))

        try:
            with smtplib.SMTP_SSL(SERVER, PORT) as server:
                server.connect(SERVER, PORT)
                server.login(USER, PASSWORD)
                server.sendmail(FROM_EMAIL, TO, msg.as_string())
            print(f"Email sent successfully on {current_date}!")

        except smtplib.SMTPException as e:
            print(f"Failed to send email on {current_date}: {e} ")

        except Exception as e:
            print(f"An unexpected error occurred on {current_date}: {e}")

        old_peers = lista_peer
        time.sleep(((datetime.datetime.now(pytz.timezone(TIMEZONE)).replace(hour=0, minute=0, second=0,
                                                                            microsecond=0) + datetime.timedelta(
            days=1)) - datetime.datetime.now(pytz.timezone(TIMEZONE))).total_seconds())
    print(f"Email not sent on {current_date}: same peers of yesterday.")
