"""
1. Use the iterparse to iteratively step through each top level element in XML
2. Shaping each element into certain data structures
3. Write each data structure to the appropriate csv files
Reference: this code was modified from
'Case study: OpenStreetMap Data[SQL] Quiz 11'
Note: validation was run on 'sample.osm' and no response was obtained,
      indicating that the output structure matches the structure in schema.py
      The following code is run on 'bali.osm' without validation.
"""
import csv
import codecs
import re
import xml.etree.cElementTree as ET
import pprint
import cerberus
import schema
from audit_phone_numbers import *
from audit_street_name import *
from collections import Counter,defaultdict

OSM_PATH = "bali.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches
# the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid',
               'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

def shape_element(element, node_fields=NODE_FIELDS,
                  node_tags_fields=NODE_TAGS_FIELDS,
                  way_fields=WAY_FIELDS, way_tags_fields=WAY_TAGS_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    # Handle secondary tags the same way for both node and way elements
    node_attribs, way_attribs = {}, {}
    tags, way_nodes = [], []

    #Parsing through each child element with node tag
    if element.tag == 'node':
        for node_attr in node_fields:
            node_attribs[node_attr] = element.attrib[node_attr]
        #Parsing through each lower element of the child elements with node tag
        subtags = element.iter('tag')
        if subtags:
            for tag in subtags:
                if not PROBLEMCHARS.search(tag.attrib['k']):
                    tag_dict = {}
                    tag_dict['id'] = element.attrib['id']
                    # use 'if is_street_name()' and 'if is_phone_num_'
                    # function to determine if the attribute matches
                    if is_street_name(tag):
                        tag.attrib['v']=update_name(tag.attrib['v'],
                                                    mapping_street)
                    if is_phone_num(tag):
                        tag.attrib['v']=update_phonenum(tag.attrib['v'])
                    tag_dict['value'] = tag.attrib['v']

                    if LOWER_COLON.search(tag.attrib['k']):
                        split_key = (tag.attrib['k']).split(':')
                        tag_dict['type'] = split_key[0]
                        if len(split_key) == 2:
                            tag_dict['key'] = split_key[1]
                        elif len(split_key) > 2:
                            tag_dict['key'] = ':'.join(split_key[1:])
                    else:
                        tag_dict['type'] = default_tag_type
                        tag_dict['key'] = tag.attrib['k']
                    tags.append(tag_dict)
        else:
            tags.append([])
        return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':
        #Parsing through each child element with way tag
        for way_attr in way_fields:
            way_attribs[way_attr] = element.attrib[way_attr]
        #Parsing through each lower element of the child elements with way tag
        subtags_nd = element.iter('nd')
        if subtags_nd:
            counter = 0
            for subtag_nd in subtags_nd:
                way_node_dict = {}
                way_node_dict['id'] = element.attrib['id']
                way_node_dict['node_id'] = subtag_nd.attrib['ref']
                way_node_dict['position'] = counter
                counter += 1
                way_nodes.append(way_node_dict)

        subtags = element.iter('tag')
        if subtags:
            for tag in subtags:
                if not PROBLEMCHARS.search(tag.attrib['k']):
                    tag_dict = {}
                    tag_dict['id'] = element.attrib['id']
                    # use 'if is_street_name()' and 'if is_phone_num_'
                    # function to determine if the attribute matches
                    if is_street_name(tag):
                        tag.attrib['v']=update_name(tag.attrib['v'],
                                                    mapping_street)
                    if is_phone_num(tag):
                        tag.attrib['v']=update_phonenum(tag.attrib['v'])

                    tag_dict['value'] = tag.attrib['v']
                    #Checking if the 'k' attribute is 'address'
                    if tag.attrib['k'].strip() == "address":
                        print 'k attribute is address with the following value:'
                        print tag.attrib['v']
                    if LOWER_COLON.search(tag.attrib['k']):
                        split_key = (tag.attrib['k']).split(':')
                        tag_dict['type'] = split_key[0]
                        if len(split_key) == 2:
                            tag_dict['key'] = split_key[1]
                        elif len(split_key) > 2:
                            tag_dict['key'] = ':'.join(split_key[1:])
                    else:
                        tag_dict['type'] = default_tag_type
                        tag_dict['key'] = tag.attrib['k']
                tags.append(tag_dict)
        else:
            tags.append([])

        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}'" 
                         "has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for
            k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)
