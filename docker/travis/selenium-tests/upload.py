# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest
import requests


class Upload(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def test_upload(self):
        self.get_data()
        sel = self.browser

        # Try logging in first
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

        # Then try to upload a layer
        sel.get("http://localhost/layers/?limit=100&offset=0")
        sel.find_element_by_link_text("Upload Layers").click()
        WebDriverWait(sel, 10).until(
            EC.title_contains("Upload Layer")
        )
        upload = sel.find_element_by_id("file-input")
        upload.send_keys("/tmp/rivers.shp")
        upload.send_keys("/tmp/rivers.shx")
        upload.send_keys("/tmp/rivers.dbf")
        upload.send_keys("/tmp/rivers.prj")
        sel.find_element_by_id("upload-button").click()
        element = WebDriverWait(sel, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert"))
        )
        sel.get("http://localhost:32771/layers/geonode:rivers")

    def get_data(self):
        chunk_size = 4096
        shp = ('https://www.github.com/geonode/geonode/docs/tutorials/devel/'
         'geonode_apis/geoserver_rest/examples/resources/shapefiles/rivers.shp')
        r = requests.get(shp, stream=True)
        with open("/tmp/rivers.shp", 'wb') as fd:
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)
        shx = ('https://www.github.com/geonode/geonode/docs/tutorials/devel/'
         'geonode_apis/geoserver_rest/examples/resources/shapefiles/rivers.shx')
        r = requests.get(shx, stream=True)
        with open("/tmp/rivers.shx", 'wb') as fd:
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)
        dbf = ('https://www.github.com/geonode/geonode/docs/tutorials/devel/'
         'geonode_apis/geoserver_rest/examples/resources/shapefiles/rivers.dbf')
        r = requests.get(dbf, stream=True)
        with open("/tmp/rivers.dbf", 'wb') as fd:
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)
        prj = ('https://www.github.com/geonode/geonode/docs/tutorials/devel/'
         'geonode_apis/geoserver_rest/examples/resources/shapefiles/rivers.prj')
        r = requests.get(prj, stream=True)
        with open("/tmp/rivers.prj", 'wb') as fd:
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)

    def tearDown(self):
        self.browser.quit()

if __name__ == "__main__":
    unittest.main()
