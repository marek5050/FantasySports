import unittest
from HelloWorld import HelloWorld

class MyTestCase(unittest.TestCase):
  def test_default_greeting_set(self):
    hw = HelloWorld()
    self.assertEqual(hw.message, 'Hello world!')

if __name__ == '__main__':
  unittest.main()