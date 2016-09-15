# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest


class LogIn(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def test_log_in(self):
        sel = self.browser
        sel.get("http://localhost/account/login/?next=/")
        self.assertIn("example.com", sel.title)
        user = sel.find_element_by_id("id_username")
        user.send_keys("admin")
        passwd = sel.find_element_by_id("id_password")
        passwd.send_keys("exchange")
        sel.find_element_by_css_selector("form > button.btn-primary").click()
        WebDriverWait(sel, 10).until(
            EC.title_contains("Welcome")
        )

    def tearDown(self):
        self.browser.quit()

if __name__ == "__main__":
    unittest.main()
