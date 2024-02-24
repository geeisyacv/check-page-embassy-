from email import message
import requests
import smtplib
from email.mime.text import MIMEText
import yaml
import schedule
import time
from datetime import datetime
from bs4 import BeautifulSoup


# Replace 'https://example.com' with the URL of the page you want to check
url_base = "https://www.citaconsular.es/es/hosteds/widgetdefault/2096463e6aff35e340c87439bc59e410c/bkt859859"
headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"
}

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


def check_page_online(url, headers):
    """Check if the given URL is online and print the page title if it is.

    Args:
        url (str): URL of the page to check.
        headers (dict): Headers to use for the request.

    Returns:
        str or None: Title of the page if online, otherwise None.
    """
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        
        html_content = response.content
        soup = BeautifulSoup(html_content, "html.parser")
        title = soup.title.text if soup.title else None
        return title

    except requests.HTTPError as http_err:
        print(f"The page {url} is not online. HTTP error occurred: {http_err}")
    except requests.RequestException as req_err:
        print(f"An error occurred: {req_err}")
    
    return None


def send_notification_email(
    config,
):
    subject = config["email"]["subject"]
    recipient_email = config["email"]["to"]
    body = config["email"]["body"]
    send_email(config, subject, recipient_email, body)


def main():
    config = load_config()
    if not config:
        print("Failed to load configuration.")
        return

    while True:
        page_content = check_page_online(url_base,headers)
        if page_content:
            print("The page is online. " + str(datetime.now()))
            send_notification_email(config)
        else:
            print("The page isn't online." + str(datetime.now()))

        time.sleep(180)  # Sleep for 3 minutes


if __name__ == "__main__":
    main()
