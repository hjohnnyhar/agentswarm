import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    anthropic_api_key: str = ""
    gmail_address: str = "hjohnnyharai@gmail.com"
    recipient_email: str = "hjohnnyharai@gmail.com"
    gmail_app_password: str = ""

    def __post_init__(self):
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not self.anthropic_api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY is not set. "
                "Export it or add to a .env file in the project root."
            )
        self.gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD", "")
