import sys
import csv
import json
import re
import math

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
	base_form_name = '';
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
		primary_key_counter = 0;
		if form_name.find('~') != -1:
			form_name,fk_name = form['form name'].split('~');
			form_dict[form_name] = fk_name;
			numRepeats = form_name.split(' ')[1];
		else:
			base_form_name = form['form name'];
			form_dict = {};
		for line in reader:
			pk_num += 1;
			keys = line.keys();
			fixtureDict = {};
			if numRepeats:
				if numRepeats.isdigit() is False:
					"""
					Handles special case where the number of repeats depends
					on another field, usually labeled as formName [relativeForm].
					This field will not be in the form[fields] list. 
					form_name is changed to avoid errors regarding the number 
					of repeats as the code continues, specifically an error
					might pop up in find_related_forms if it is not changed to a
					number.
					"""
					new_num_repeats = line[numRepeats.replace('[','').replace(']','')];
					if not new_num_repeats:
						new_num_repeats = 0;
					#form_name is formatted like formName 5~otherForm 5 before
					#this change
					new_form_name = form_name.split('~')[0].split(' ')[0] + 											' ' + str(new_num_repeats);
					form_dict[new_form_name] = fk_name;
				if new_form_name:	
					foreign_forms_list=find_related_forms(new_form_name,form_dict);
					new_form_name = '';
				else:
					foreign_forms_list=find_related_forms(form_name,form_dict);
				full_form_list = foreign_forms_list[:];
				full_form_list.append(base_form_name);
				full_form_list = full_form_list[::-1];
				primary_key_counter = generate_repeating_fixtures(line,form,foreign_forms_list,fixtures,fixtureDict,keys,pk_num_list,pk_num,primary_key_counter,[],full_form_list);
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
						field_names = get_field_names(field,form_dict);
						checked_line = '';
						answered = '';
						for name in field_names:
							if name in keys:
								if len(field_names) > 1:
									if line[name] == '1':
										checked_line = name[-1];
										answered = True;
									elif line[name] == '0':
										answered = True;
								else:	
									if line[name]:
										checked_line = line[name];
						if checked_line:
							fixtureDict[field['field name']]=[field,checked_line];
						elif answered is True:
							fixtureDict[field['field name']]=[field,'0'];
						else:
							fixtureDict[field['field name']]=[field,''];
					elif field['field name'].lower() in keys:
						fixtureDict[field['field name']] = [field,line[field['field name']]];
				fixtures.append([form_name, fixtureDict]);
	printFixtures(fixtures,pk_num_list,fout);

def generate_repeating_fixtures(line,form,form_list,fixtures,fixtureDict,keys,pk_num_list,pk_num,primary_key_counter,repeats_num_list=[],full_form_list=None):
	
	"""
	Getting the number of repeats from last value in list because that is the 
 	least nested form
	"""
	repeats = int(form_list[-1].split(' ')[1]);
	for i in range(repeats):
		#repeats_num_list keeps track of the number of iterations the recursion has gone through in each element
		repeats_num_list.append(i+1);
		if len(form_list[:-1]) > 0:
			primary_key_counter = generate_repeating_fixtures(line,form,form_list[:-1],fixtures,fixtureDict,keys,pk_num_list,pk_num,primary_key_counter,repeats_num_list,full_form_list);
		else:
			primary_key_counter += 1;
			fixtureDict = {};
			fk_index = full_form_list.index(form_list[0]) - 1;
			foreign_key = full_form_list[fk_index].lower().split(' ')[0];
			if fk_index == 0:
				fixtureDict[foreign_key] = ['',pk_num];
			else:	
				fixtureDict[foreign_key] = ['',int(math.ceil(primary_key_counter/float(repeats)))];
			pk_num_list.append(primary_key_counter);
			for field in form['fields']:
				clean_field_name = re.sub('\${d\}','',field['field name']);
				#removed first element(base form) from full_form_list for naming
				field_name = get_field_name(field,full_form_list[1:],repeats_num_list);
				if field['choices']:
					field_names = get_field_names(field,full_form_list[1:],field_name);
					checked_line = '';
					answered = '';
					for name in field_names:
						if name in keys:
							if len(field_names) > 1:
								if line[name] == '1':
									checked_line = name[-1];
									answered = True;
								elif line[name] == '0':
									answered = True;
							else:
								if line[name]:
									checked_line = line[name];
					if checked_line:			
						fixtureDict[clean_field_name]=[field,checked_line];
					elif answered is True:
						fixtureDict[clean_field_name]=[field,'0'];
					else:
						fixtureDict[clean_field_name]=[field,''];
				elif field_name.lower() in keys:
					fixtureDict[field_name] = [field,line[field_name]];
			clean_form_name = form['form name'].split(' ')[0].replace('$','');
			fixtures.append([clean_form_name, fixtureDict]);
		repeats_num_list.pop();
	return primary_key_counter;

def get_field_name(field,form_list,repeat_num_list):
	prefix = '';
	for i in range(len(form_list)):
		if form_list[i] != form_list[-1]:
			str_split = form_list[i].split(' ');
			name = str_split[0];
			num_repeats = repeat_num_list[i];
			prefix = name.replace('$',str(num_repeats));
			prefix = prefix + '_';
		elif field['field name'].find('${d}') != -1:
			field_name = re.sub('\$\{d\}',str(repeat_num_list[-1]),field['field name']);
		else:
			field_name = field['field name'] + '' + str(repeat_num_list[-1]);
	field_name = prefix + field_name;
	return field_name;
	
def find_related_forms(form_name,form_list,foreign_forms=None):
	if foreign_forms is None:
		foreign_forms = [];
	if form_name in form_list and not form_name in foreign_forms:
		foreign_forms.append(form_name);
		find_related_forms(form_list[form_name],form_list,foreign_forms);
	return foreign_forms;

def get_field_names(field,form_dict,field_name=None):
	"""
	Checkboxes and radio_other fields have multiple parts in the data csv, usually something like
	name1 name2 name3 for each checkbox/radio button that is pushable, but the info must be put
	into one field.

	This method finds the fields in the data file that are related to the field parameter. If it
	is a checkbox, it splits the possible choices and uses that to find the fields.
	If it is a radio_other field type, splits choices and uses that info to find the field.
	"""
	if field_name == None:
		field_name = field['field name'];
	choices_field_names = [];
	if field['field type'] == 'checkbox':
		choices = field['choices'].split('|');
		if form_dict:
			for choice in choices:
				choices_field_names.append(field_name.lower() + '___' + choice.split(',')[0].strip(' '));
		else:
			for choice in choices:
				choices_field_names.append(field_name.lower() + '___' + choice.split(',')[0].strip(' '));
	else:
		choices_field_names.append(field_name.lower());		
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
	"""
	fixturesList is a list of lists. Each element is a list of [form name,fixtureDict]
	Each element in fixtureDict is [field, field_val]
	"""
	allJson = [];
	firstFix = True;
	for i in range(len(fixturesList)):
		fieldDict = {};
		#if field has a value, print it
		for key in fixturesList[i][1]:
			if fixturesList[i][1][key]:
				field = fixturesList[i][1][key][0];
				field_val = fixturesList[i][1][key][1];
				if field:
					fieldDict[key] = cast_field(field,field_val);
				else:
					#if it is just a foreign key
					fieldDict[key] = field_val;
		allJson.append(	{'model': 'mysite.' + fixturesList[i][0] + '',
			'pk': pkList[i],
			'fields': fieldDict
			});
	fout.write(json.dumps(allJson,indent=4,separators=(',',': ')));

def get_field_type(field):
	"""
        Given the database connection, the table name, and the cursor row description,
        this routine will return the given field type name, as well as any additional keyword
        parameters and notes for the field.
        """
        required = field['required'];
        validation_type = field['validation type'];
        field_type = field['field type'];

        try:
                field_type = field_types.get(validation_type, field_types[field_type]);
        except KeyError:
                field_type = 'TextField';
        if not required:
                if field_type is 'BooleanField':
                        field_type = 'NullBooleanField';

        choices = None;
        if field['choices']:
                try:
                        choices = [(int(v.strip()), k.strip()) for v, k in [choice.split(',') \
                                for choice in field['choices'].split('|')]]
                        field_type = 'IntegerField'
                except (ValueError, TypeError):
                        pass

        return field_type;

def cast_field(field,field_val):
	"""
	Casts line[name] depending on the field_type
	"""
	field_type = get_field_type(field);
	if field_type == 'CharField' or field_type == 'TextField':
		return str(field_val);
	elif field_type == 'IntegerField':
		if field_val and field_val.isdigit():
			return int(field_val);
	elif field_type == 'FloatField':
		try:
			return float(field_val);
		except:
			pass;
	elif field_type == 'NullBooleanField':
		if field_val == '':
			return None;
		elif field_val == '0':
			return False;
		elif field_val == '1':
			return True;
		else:
			return field_val;
	elif field_type == 'BooleanField':
		if field_val:
			if field_val == '1':
				return True;
			elif field_val == '0':
				return False;
			else:
				return field_val;
	else:
		return field_val;
if len(sys.argv) == 3:
	readHeader(sys.argv[1],sys.argv[2]);
else:
	readHeader();
