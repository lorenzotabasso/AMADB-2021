import unittest

from projects.Relational.MariaDBConnector import MariaDBConnector


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()

    mariaDB = MariaDBConnector()
