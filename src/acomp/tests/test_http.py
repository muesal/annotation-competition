import os
import tempfile
from unittest import TestCase
from acomp import app, db


class TestHttp(TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.tmpf, self.tmpdb = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + self.tmpdb
        self.app = app.test_client()
        db.create_all()
        self.assertFalse(app.debug)

    def test_http_index_ok(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        db.drop_all()
        os.close(self.tmpf)
        os.unlink(self.tmpdb)
