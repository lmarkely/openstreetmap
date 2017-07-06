'''
1. Use the iterative parsing to process the map file.
2. Identify what tags and subtags are in the file, as well as how many they are.
3. Identify the attributes of child and lower level elements
4. Return a dictionary with the tag name as the key
   and the number of times this tag is encountered in the map as the value.
'''
import csv
import codecs
import re
import xml.etree.cElementTree as ET
import pprint
import cerberus
import schema
from collections import Counter,defaultdict
OSMFILE = 'bali.osm'

def count_tags(elem):
    '''
    For each input element, return a dict with the name of tags
    in the lower level elements as keys and frequency as values.
    Args:
        elem: element of xml file
    Returns:
        tag_dict (dict): keys = tags, values = frequency of tags
    '''
    tag_dict = {}
    for sub_elem in elem:
        tag_dict[sub_elem.tag] = tag_dict.get(sub_elem.tag,0) + 1
    return tag_dict

def elem_attrib(elem):
    '''
    For each input element, return a dict with the name of tags
    in the lower level elements as keys and attributes as values.
    Args:
        elem: element of xml file
    Returns:
        attrib_dict (dict): keys = tags, values = attributes
    '''
    attrib_dict = {}
    for sub_elem in elem:
        if sub_elem.tag not in attrib_dict:
            attrib_dict[sub_elem.tag] = sub_elem.attrib.keys()
        else:
            for attrib in sub_elem.attrib:
                if attrib not in attrib_dict[sub_elem.tag]:
                    attrib_dict[sub_elem.tag].append(attrib)
    return attrib_dict

def merge_dict(dict1,dict2):
    '''
    Args:
        dict1 (dict): one of the two dictionaries
        dict2 (dict): one of the two dictionaries
    Returns:
        dict: merged dict1 and dict2
    Reference: this code was copied and modified from
    https://stackoverflow.com/questions/1495510/
    combining-dictionaries-of-lists-in-python
    '''
    keys = set(dict1).union(dict2)
    no = []
    return dict((key,list(set(dict1.get(key,no)+dict2.get(key,no))))
                for key in keys)

def explore():
    tree = ET.parse(OSMFILE)
    root = tree.getroot()
    child_tags = count_tags(root)

    print('Tags and their frequency in the child elements:')
    pprint.pprint(child_tags)

    print('\nTags and attributes of the child elements:')
    child_attrib = elem_attrib(root)
    pprint.pprint(child_attrib)

    sub_tags, tag_attrib, sub_tags_attrib = {}, {}, {}
    for key in child_tags.keys():
        sub_tags[key] = Counter({})
        sub_tags_attrib[key] = {}

    for child in root:
        if child.iter():
            sub_tags[child.tag] += Counter(count_tags(child))
            sub_tags_attrib[child.tag] = merge_dict(sub_tags_attrib[child.tag],
                                                    elem_attrib(child))

    print(
    '\nDictionary of tags and their frequency in the lower level elements:')
    pprint.pprint(sub_tags)

    print(
    '\nDictionary of tags and their attributes in the lower level elements:')
    pprint.pprint(sub_tags_attrib)
