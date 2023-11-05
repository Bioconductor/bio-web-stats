"""TODO.

See: http://webtest.readthedocs.org/
"""

from bioc_webstats.stats import URI_PATH_PREFIX


class TestPages:
    """TODO."""

    def test_can_log_in_returns_200(self, webapp):
        """Login successful."""
        # Goes to homepage
        res = webapp.get(URI_PATH_PREFIX + "/")

        assert res.status_code == 200
