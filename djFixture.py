import sys
import csv
import json
import re

field_types = {
        'date_ymd': 'DateField',
        'number': 'FloatField',
        'integer': 'IntegerField',
        'email': 'EmailField',
        'text': 'CharField',
        'textarea': 'TextField',
        'calc': 'FloatField',
        'radio': 'CharField',
        'select': 'CharField',
        'checkbox': 'CharField',
        'yesno': 'BooleanField',
        'truefalse': 'BooleanField',
}

def inspect(file,reader, jsonModels,fout):
	form_name = '';
	pk_num_list = [];
	fixtures = [];
	form_dict = {};
	for form in open(jsonModels,'r'):
		pk_num = 0;
		form = json.loads(form);
                form_name = form['form name'];
		file.seek(0);
		reader.next();
		numRepeats = '';
		if form_name.find('~') != -1:
			form_name,fk_name = form['form name'].split('~');
			numRepeats = form_name.split(' ')[1];
			form_dict[form_name] = fk_name;
		else:
			print form_dict;
			form_dict = {};
		for line in reader:
			pk_num += 1;
			keys = line.keys();
			fixtureDict = {};
			if form['form name'].find('~') != -1:
                                fixtureDict[fk_name.lower()] = pk_num;
			if numRepeats:
				if numRepeats.isdigit() is False:
					#Then the number of repeats depends on a field
					numRepeats = line[numRepeats.replace('[','').replace(']','')];
					if not numRepeats:
						numRepeats = 0;
				for i in range(int(numRepeats)):
					pk_num_list.append(i+1);
					for field in form['fields']:
						field_type = get_field_type(field);
						if field['choices']:
							field_names = get_field_names(field,keys,form_dict);
							for name in field_names:
								if name in keys:
									if line[name] == '1':
										fixtureDict[field['field name']] = name[-1];
						elif field['field name'].lower() in keys:
							fixtureDict[field['field name']] = cast_field(line,										field_type,field['field name'].lower());
					fixtures.append([form_name,fixtureDict]);
			else:
				pk_num_list.append(pk_num);
				for field in form['fields']:
					field_type = get_field_type(field);
					"""
					Determines if there are choices in the field, 
					what they are, and gets the
					value for each of those fields that includes the choices
					"""
					if field['choices']:
						field_names = get_field_names(field,keys,form_dict);
						for name in field_names:
							if name in keys:
								if line[name] == '1':
									fixtureDict[field['field name']] = 												name[-1];
					elif field['field name'].lower() in keys:
						fixtureDict[field['field name']] = cast_field(line,field_type,								field['field name'].lower());
			
				fixtures.append([form_name, fixtureDict]);
	printFixtures(fixtures,pk_num_list,fout);

def get_field_names(field,keys,form_dict):
	"""
	Checkboxes and radio_other fields have multiple parts in the data csv, usually something like
	name1 name2 name3 for each checkbox/radio button that is pushable, but the info must be put
	into one field.

	This method finds the fields in the data file that are related to the field parameter. If it
	is a checkbox, it splits the possible choices and uses that to find the fields.
	If it is a radio_other field type, splits choices and uses that info to find the field.
	"""
	choices_field_names = [];
	
	if 
	
	

	if field['field type'] == 'checkbox':
		choices = field['choices'].split('|');
		if form_dict:
			for choice in choices:
				choices_field_names.append(field['field name'].lower() + choice.split(',')[0].strip(' ') + '___' + choice.split(',')[0].strip(' '));
		else:
			for choice in choices:
				choices_field_names.append(field['field name'].lower() + '___' + choice.split(',')[0].strip(' '));
	elif field['field type'] == 'radio_other':
		choices = field['choices'].split('|');
		for choice in choices:
			choices_field_names.append(field['field name'].lower() + choice.split(',')[0].strip(' '));
	else:
		choices_field_names.append(field['field name'].lower());		

	return choices_field_names;	

def has_field_type(form, field_type):
	#determines if a form has a field with field_type
	for field in form['fields']:
		if field['field type'] == field_type:
			return field;
	return '';
	
def readHeader(file=None,jsonFile=None):
	if not file:
		file = raw_input('Enter a valid filename: ');
	
	if not jsonFile:
		jsonFile = raw_input('Enter the json filename: ');
	
	fin = open(file);
	headers = fin.readline().split(',')
	dialect = csv.Sniffer().sniff(fin.read(1024));
	reader = csv.DictReader(fin, fieldnames=headers,dialect=dialect);
	reader.next();

	fout = open('fixtures','w+');

	inspect(fin,reader,jsonFile,fout);

def printFixtures(fixturesList,pkList,fout):
	allJson = [];
	firstFix = True;
	for i in range(len(fixturesList)):
		fieldDict = {};
		for field in fixturesList[i][1]:
			if fixturesList[i][1][field]:
				fieldDict[field] = fixturesList[i][1][field];
		#check if foreign key isnt only key in dict
		onlyFK = False;
		if len(fieldDict.keys()) == 1 and 'foreignkey' in fieldDict:
			onlyFK = True;
		allJson.append(	{'model': 'mysite.' + fixturesList[i][0] + '',
			'pk': pkList[i],
			'fields': fieldDict
			});
	fout.write(json.dumps(allJson,indent=4,separators=(',',': ')));

def get_field_type(line):
	"""
        Given the database connection, the table name, and the cursor row description,
        this routine will return the given field type name, as well as any additional keyword
        parameters and notes for the field.
        """
        required = line['required'];
        validation_type = line['validation type'];
        field_type = line['field type'];

        try:
                field_type = field_types.get(validation_type, field_types[field_type]);
        except KeyError:
                field_type = 'TextField';
        if not required:
                if field_type is 'BooleanField':
                        field_type = 'NullBooleanField';

        choices = None;
        if line['choices']:
                try:
                        choices = [(int(v.strip()), k.strip()) for v, k in [choice.split(',') \
                                for choice in line['choices'].split('|')]]
                        field_type = 'IntegerField'
                except (ValueError, TypeError):
                        pass

        return field_type;

def cast_field(line,field_type,name):
	"""
	Casts line[name] depending on the field_type
	"""
	if field_type == 'CharField' or field_type == 'TextField' or field_type == 'BooleanField':
		return str(line[name]);
	elif field_type == 'IntegerField':
		if line[name]:
			return int(line[name]);
		#else:
			#return 0;
	elif field_type == 'FloatField':
		return line[name];
	else:
		return line[name];
if len(sys.argv) == 3:
	readHeader(sys.argv[1],sys.argv[2]);
else:
	readHeader();
