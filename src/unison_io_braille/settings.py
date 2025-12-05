import os

APP_NAME = "unison-io-braille"
ORCH_HOST = os.getenv("UNISON_ORCH_HOST", "orchestrator")
ORCH_PORT = os.getenv("UNISON_ORCH_PORT", "8080")
DEFAULT_PERSON_ID = os.getenv("UNISON_DEFAULT_PERSON_ID", "local-user")
REQUIRED_SCOPE_INPUT = os.getenv("UNISON_BRAILLE_SCOPE_INPUT", "braille.input.read")
