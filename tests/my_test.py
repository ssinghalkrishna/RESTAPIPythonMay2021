import json
import unittest
import requests

from lib.authentication import Authenticate


class YahooAPITestCase(unittest.TestCase):
    def test_for_successful_response(self):
        r = requests.get("https://yahoo.com")
        self.assertEqual(r.status_code, 200)
        self.assertTrue('OK' == r.reason)


class CareerPortalTests(unittest.TestCase):
    def setUp(self) -> None:
        pass
        # if don't put self above, base_url is local variable, not available outside

    def test_login(self):
        sess = Authenticate() #invoking constructor to make object of class. sess is pointer to that object.
        positions = sess.get_all_positions()
        json_positions = json.loads(positions.text)
        self.assertGreater(len(json_positions), 5)

        result = sess.authenticate('student@example.com', 'welcome')
        self.assertEqual(200, result.status_code)
        json_parsed = json.loads(result.text)
        self.assertTrue(json_parsed['authenticated'])

        verify_response = sess.perform_user_verification()
        verify_content = json.loads(verify_response.content)
        user_id = verify_content['id']
        email = verify_content['email']
        self.assertTrue(email == 'student@example.com')
        self.assertEqual(8, user_id)

        my_positions = sess.get_candidate_positions(user_id)
        json_my_positions = json.loads(my_positions.text)
        self.assertEqual(len(json_my_positions), 5)

    def test_cannot_login(self):
        sess = Authenticate()
        response = sess.authenticate('foo', 'barr')
        json_parsed = json.loads(response.text)
        self.assertEqual('Incorrect email: foo', json_parsed['errorMessage'])


if __name__ == '__main__':
    unittest.main()
