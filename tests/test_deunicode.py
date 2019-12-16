"""
Show that the unicode conversion to UTF-8 works
"""
import unittest

from functools import reduce

import ospsurvey.deunicode

class TestDeunicode(unittest.TestCase):

  def test_decode_list(self):

    unicode_list = [u'a', 'b', 2]
    
    a = ospsurvey.deunicode.decode_list(unicode_list)

    # make sure all elements are not unicode
    result = reduce(
      lambda a,b : a and b,
      [not isinstance(t, unicode) for t in a]
    )
    self.assertEqual(result, True)
    

  def test_decode_dict(self):

    unicode_dict = {
      u'hello': u'there',
      u'but': 3,
      u'because': "just"
    }

    a = ospsurvey.deunicode.decode_dict(unicode_dict)

    # all keys are not unicode
    k = reduce(
      lambda a,b : a and b,
      [not isinstance(t, unicode) for t in a.keys()]
    )
    
    # all values are not unicode
    v = reduce(
      lambda a,b : a and b,
      [not isinstance(t, unicode) for t in a.values()]
    )

    self.assertEquals(True, k and v)
