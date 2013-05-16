import sys
import csv
import json

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
	fixtures = [];
	pk_num_list = [];
	for form in open(jsonModels,'r'):
		pk_num = 0;
		form = json.loads(form);
                form_name = form['form name'];
		file.seek(0);
		reader.next();
		for line in reader:
			pk_num += 1;
			pk_num_list.append(pk_num);
			keys = line.keys();
			fixtureDict = {};
			for field in form['fields']:
				field_type = get_field_type(field);
				"""
				Determines if there are choices in the field, 
				what they are, and gets the
				value for each of those fields that includes the choices
				"""
				if field['choices']:
					choices_field_names = readChoices(field,keys);
					for name in choices_field_names:
						if name in keys:
							fixtureDict[field['field name']] = line[name]
				elif field['field name'] in keys:
					fixtureDict[field['field name']] = cast_field(line,field_type,field['field name']);
				else:
					fixtureDict[field['field name']] = 'Missing field data';	
			fixtures.append([form_name, fixtureDict]);	
	printFixtures(fixtures,pk_num_list,fout);
		
def readChoices(field,keys):
	choices_field_names = [];
	if field['field type'] == 'checkbox':
		choices = field['choices'].split('|');		
		for choice in choices:
			
			choices_field_names.append(field['field name'] + '___' + choice.split(',')[0].strip(' '));
	elif field['field type'] == 'radio_other':
		choices = field['choices'].split('|');
		for choice in choices:
			choices_field_names.append(field['field name'] + choice.split(',')[0].strip(' '));
	else:
		choices_field_names.append([field['field name']]);		

	return choices_field_names;	
	
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
	if field_type == 'CharField' or field_type == 'TextField' or field_type == 'BooleanField':
		return str(line[name]);
	elif field_type == 'IntegerField':
		if line[name]:
			return int(line[name]);
		else:
			return 0;
	elif field_type == 'FloatField':
		return line[name];
	else:
		return line[name];
if len(sys.argv) == 3:
	readHeader(sys.argv[1],sys.argv[2]);
else:
	readHeader();
