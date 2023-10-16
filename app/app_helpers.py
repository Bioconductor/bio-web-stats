"""Utility functions for the Flask app.
"""

from datetime import datetime,date

# TODO: allow for mocking this class
class app_config:
    """# The `_summary_` is a placeholder for a summary or description of the `app_config` class.
    # It is typically used to provide a brief explanation of what the class does or its
    # purpose. In this case, it seems like the summary is missing or incomplete.
    _summary_
    """   
    def today() -> date:
        """ Return today's date (or mocked date if in test mode)"""
        return datetime.now().date()