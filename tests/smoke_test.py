"""
Just checks that the package can be imported
"""

import unittest


class TestSmoke(unittest.TestCase):
    def test_import(self):
        import neurosym

        self.assertTrue(True)
