from unittest import TestCase
from acomp.prefill import calc_checksum, normalize_fileext
from acomp import app
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
app.secret_key = '01234test'
test_gif_path = os.path.join(THIS_DIR, 'test_data/test.gif')
test_jpg_path = os.path.join(THIS_DIR, 'test_data/test.jpg')
test_png_path = os.path.join(THIS_DIR, 'test_data/test.png')


class TestPrefill(TestCase):
    def test_calc_checksum(self):
        # openssl dgst -sha3-256 <(cat test_data/test.png; printf '01234test')
        self.assertEqual(calc_checksum(test_gif_path), '21cf19e58108c0fbc4ceeddfad8824621c3be27267f47ef7a76385c737110867')
        self.assertEqual(calc_checksum(test_jpg_path), '7c638edce383b698d721a66db41cdac416a7d878e47e792a4978aa97ac7cef61')
        self.assertEqual(calc_checksum(test_png_path), 'b674f49f6cbf9fa0a9ea905b696d6a9e17f4189e23ac78f4f9e9c8f984033f7c')


    def test_normalize_fileext(self):
        self.assertEqual(normalize_fileext('test.jpeg'), '.jpg')
        self.assertEqual(normalize_fileext('test.jpg'), '.jpg')
        self.assertEqual(normalize_fileext('test.png'), '.png')
