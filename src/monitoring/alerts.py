import requests
import os
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


def send_email_alert(subject, body, to_emails):
    """
    Send an email alert using the Mailgun API.
    """
    try:
        mailgun_api_key = os.getenv("MAILGUN_API_KEY")
        if not mailgun_api_key:
            raise ValueError("Mailgun API key not found in environment variables")

        response = requests.post(
            "https://api.mailgun.net/v3/sandbox96338a266b544d14be5f1ba2b8749232.mailgun.org/messages",
            auth=("api", mailgun_api_key),
            data={
                "from": "AI Monitoring Alert <mailgun@sandbox96338a266b544d14be5f1ba2b8749232.mailgun.org>",
                "to": to_emails,
                "subject": subject,
                "text": body,
            },
        )
        response.raise_for_status()
        logger.info("Email alert sent successfully via Mailgun")
    except Exception as e:
        logger.error(f"Failed to send email alert via Mailgun: {e}")


def check_test_results(test_suite, tags):
    """
    Check the test results for failures and return a boolean flag.
    """
    if "main" in tags and "single" in tags:
        test_results = test_suite.as_dict()
        failed_tests = [test for test in test_results["tests"] if test["status"].lower() in ["fail", "error"]]
        return bool(failed_tests), failed_tests
    return False, []


def generate_alert_message(all_failed_tests, config):
    """
    Generate an alert message for the failed tests.
    """
    message = f"Alert: Test failures detected in {config['info']['project_name']} project.\n\n"
    for category, failed_tests in all_failed_tests.items():
        message += f"Category: {category}\n"
        for test in failed_tests:
            message += f"Test: {test['name']}\n"
            message += f"Description: {test['description']}\n"
            message += f"Status: {test['status']}\n\n"
        message += "\n"
    return message


class AlertCollector:
    def __init__(self, config):
        """
        Initialize the alert collector with an empty dictionary to store failed tests
        """
        self.all_failed_tests = defaultdict(list)
        self.config = config

    def add_failed_tests(self, category, failed_tests):
        """
        Add failed tests to the all_failed_tests dictionary
        """
        self.all_failed_tests[category].extend(failed_tests)

    def should_alert(self):
        """
        Check if there are any failed tests to send an alert
        """
        return bool(self.all_failed_tests)

    def get_alert_message(self):
        """
        Generate the alert message to send
        """
        return generate_alert_message(self.all_failed_tests, self.config)

    def send_alert(self, to_emails):
        """
        Send an email alert if there are failed tests
        """
        if self.should_alert():
            subject = f"AI Monitoring Alert: Test Failures Detected in {self.config['info']['project_name']}"
            body = self.get_alert_message()
            send_email_alert(subject, body, to_emails)
            self.all_failed_tests.clear()  # Clear after sending
