import os
import sys
import re
from cStringIO import StringIO
from django.test import TestCase
from django.core.management import call_command
from itertools import izip
from itertools import izip_longest

__all__ = ('FixtureTestCase',)


def get_filename(filename):
    return os.path.join(os.path.dirname(__file__), 'fixtures', filename)


def search_num(self, line):
    pattern = re.compile('\d+(\.\d+)?')
    search_results = pattern.search(line);
    if search_results:
        line_num = float(search_results.group(0))
    else:
        raise TypeError("Cannot convert to a float")

def split_assert(self, line1, line2):
    data1 = line1.rstrip('\n').replace(" ","").replace(",","").split(':')
    data2 = line2.rstrip('\n').replace(" ","").replace(",","").split(':')

    
    try:
        self.assertEqual(line1,line2);
    except AssertionError:
        self.assertEqual(data1[0],data2[0]);
        try:
            self.assertAlmostEqual(float(data1[1]),float(data2[1]));
        except IndexError:
            pass;

class FixtureTestCase(TestCase):
    def test_csv_with_repeating_fields(self):
        fileName = 'fixture_with_rep_fields';
        csv_fileName1 = fileName + '.csv';
        csv_fileName2 = fileName + '.json';
        cmp_fileName = 'cmp_' + fileName + '.json';
        call_command('fixture','inspect',get_filename(csv_fileName1),
                                get_filename(csv_fileName2),'mysite');
        cmp_file = open(get_filename(cmp_fileName));
        for line1, line2 in izip(open(get_filename('fixtures.json'),'r'),
                                    open(get_filename(cmp_fileName),'r')):
            split_assert(self,line1,line2);
    def test_csv_without_repeating_fields(self):
        fileName = 'fixture_without_rep_fields';
        csv_fileName1 = fileName + '.csv';
        csv_fileName2 = fileName + '.json';
        cmp_fileName = 'cmp_' + fileName + '.json';
        call_command('fixture','inspect',get_filename(csv_fileName1),
                                get_filename(csv_fileName2),'mysite');
        cmp_file = open(get_filename(cmp_fileName));
        for line1, line2 in izip(open(get_filename('fixtures.json'),'r'),
                                    open(get_filename(cmp_fileName),'r')):
            split_assert(self,line1,line2);
