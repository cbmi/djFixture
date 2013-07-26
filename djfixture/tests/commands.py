import os
import sys
from cStringIO import StringIO
from django.test import TestCase
from django.core.management import call_command
from itertools import izip
from itertools import izip_longest

__all__ = ('FixtureTestCase',)
def get_filename(filename):
	from djfixture import tests
	return os.path.join(os.path.dirname(tests.__file__), 'fixtures', filename)

class FixtureTestCase(TestCase):
	def test_csv_with_repeating_fields(self):
		fileName = 'fixture_with_rep_fields';
       		csv_fileName1 = fileName + '.csv';
		csv_fileName2 = fileName + '.json';
        	cmp_fileName = 'cmp_' + fileName + '.json';
		call_command('fixture','inspect',get_filename(csv_fileName1),get_filename(csv_fileName2),'mysite');
        	cmp_file = open(get_filename(cmp_fileName));
		for line1, line2 in izip(open(get_filename('fixtures.json'),'r'),open(get_filename(cmp_fileName),'r')):
			line1_find = line1.find(':');
			line2_find = line2.find(':');

			label_line1 = line1[:line1_find];
			num_line1 = line1[line1_find:];
			label_line2 = line2[:line2_find];
			num_line2 =  line2[line2_find:];
			
			if num_line1:
				try:
					ret1 = int(num_line1);
				except ValueError:
					ret1 = float(num_line1);
			
			if num_line2:
				try:
					ret2 = int(num_line2);
				except ValueError:
					ret2 = float(num_line2);

			self.assertEqual(label_line1,label_line2);
			self.assertAlmostEqual(ret1,ret2);	

	def test_csv_without_repeating_fields(self):
		fileName = 'fixture_without_rep_fields';
		csv_fileName1 = fileName + '.csv';
		csv_fileName2 = fileName + '.json';
		cmp_fileName = 'cmp_' + fileName + '.json';
		call_command('fixture','inspect',get_filename(csv_fileName1),get_filename(csv_fileName2),'mysite');
		cmp_file = open(get_filename(cmp_fileName));
		for line1, line2 in izip(open(get_filename('fixtures.json'),'r'),open(get_filename(cmp_fileName),'r')):
         	       self.assertAlmostEqual(line1,line2);
