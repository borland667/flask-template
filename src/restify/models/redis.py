"""Redis keys used throughout the entire application (Flask, etc.)."""

# Email throttling.
EMAIL_THROTTLE = 'restify:email_throttle:{md5}'  # Lock.

# PyPI throttling.
POLL_SIMPLE_THROTTLE = 'restify:poll_simple_throttle'  # Lock.
