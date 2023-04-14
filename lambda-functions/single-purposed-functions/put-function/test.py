
import unittest
import app


class TestAPI(unittest.TestCase):
    def test_getApi_works(self):
        event = {'ID': 'visitors'}
        result = app.lambda_handler(event, 0)
        self.assertEqual(result['statusCode'], 200)

if __name__ == '__main__':
    unittest.main()