import unittest


class EmptyTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(EmptyTest, self).__init__(*args, **kwargs)

    def setUp(self) -> None:
        return

    def test_empty(self):
        return

    def tearDown(self) -> None:
        return


if __name__ == '__main__':
    unittest.main()