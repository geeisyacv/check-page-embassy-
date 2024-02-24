from email import message
import requests
import smtplib
from email.mime.text import MIMEText
import yaml
import schedule
import time
from datetime import datetime



def load_config(filepath="config.yml"):
    """Load configuration from a YAML file.

    Args:
        filepath (str): The path to the YAML configuration file.

    Returns:
        dict: The configuration as a dictionary if successful, None otherwise.
    """
    try:
        with open(filepath, "r") as stream:
            return yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(f"Error loading YAML config: {exc}")
        return None
    except FileNotFoundError:
        print(f"Configuration file not found: {filepath}")
        return None


# Replace 'https://example.com' with the URL of the page you want to check
url_base = "https://www.citaconsular.es/es/hosteds/widgetdefault/2096463e6aff35e340c87439bc59e410c/bkt859859"


# url_base = 'https://example.com'
def send_email(config, subject, recipient_email, body):
    sender_email = config["gmail"]["username"]
    sender_password = config["gmail"]["password"]
    host = config["gmail"]["host"]
    port = config["gmail"]["port"]

    html_message = MIMEText(body + url_base, "html")
    html_message["Subject"] = subject
    html_message["From"] = sender_email
    html_message["To"] = recipient_email

    with smtplib.SMTP_SSL(host, port) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, html_message.as_string())


def check_page_online(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"The page {url} is not online. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def send_notification_email(
    config,
):
    subject = config['email']['subject']
    recipient_email = config["email"]["to"]
    body = config["email"]["body"]
    send_email(config, subject, recipient_email, body)


def main():
    config = load_config()
    if not config:
        print("Failed to load configuration.")
        return

    while True:
        page_content = check_page_online(url_base)
        if page_content:
            print("The page is online. "+ str(datetime.now()))
            send_notification_email(config)
        else:
            print("The page isn't online."+ str(datetime.now()))
        
        time.sleep(180)  # Sleep for 3 minutes
        


if __name__ == "__main__":
    main()
