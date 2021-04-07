import unittest
from util.math import sha256, md5


class Sha256Test(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(Sha256Test, self).__init__(*args, **kwargs)

    def setUp(self) -> None:
        return

    def test_sha256(self):
        s = md5('https://www.itb.ec.europa.eu/docs/services/latest/introduction/index.html')
        print(s)
        return


    def tearDown(self) -> None:
        return


if __name__ == '__main__':
    unittest.main()
