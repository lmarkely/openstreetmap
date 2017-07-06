"""
This code fixes the phone number.
The function takes a string with phone number as an argument and
returns the fixed phone number.
There are two types of inconsistencies:
1. Inconsistent country code
2. Incorrect phone number
Reference: this code was modified from
'Case study: OpenStreetMap Data[SQL] Quiz 10'
"""
import csv
import codecs
import re
import xml.etree.cElementTree as ET
import pprint
import cerberus
import schema
from collections import Counter,defaultdict
OSMFILE = 'bali.osm'

codes = ['(+62)','(62)','(+62361)','62','p. +62','+62','0062','062','[+62]',
        '021',
        '(0361)','0361','0368',
        '080','081','082','083','085','087','089']

def is_phone_num(elem):
    '''
    Check if the element contains phone number.
    Args:
        elem: element of the xml file
    Returns:
        True if the element contains phone number information
        False otherwise
    '''
    if elem.attrib['k'] == "phone":
        if not elem.attrib['v'].startswith(tuple(codes)):
            print('Incorrect phone numbers:',elem.attrib['v'])

    return (elem.attrib['k'] == "phone" and
            elem.attrib['v'].startswith(tuple(codes)))

def audit_phonenum_type(phonenum_types, phone_num):
    '''
    Classify the phone numbers based on types of errors.
    Args:
        phonenum_types (dict): dictionary with types of errors as keys,
                                        phone numbers as values
        phone_num (string): phone number
    Returns:
        phonenum_types (dict): dictionary updated with new phone number
    '''
    for code in codes:
        if phone_num.startswith(code):
            phonenum_types[code].add(phone_num)
            return

def update_phonenum(num):
    '''
    Fix the phone numbers based on the type of errors.
    Args:
        num (string): phone number 
    Returns:
        string: corrected phone number
    '''
    code_with62 = ['62','0062','062']
    code_no62 = ['021','0361','0368',
                '080','081','082','083','085','087','089']
    if num.startswith('p. +62'):
        return num.lstrip('p. ')
    if num.startswith('('):
        for char in '()':
            num = num.replace(char,'')
    if num.startswith('['):
        for char in '[]':
            num = num.replace(char,'')
    if '(0)' in num:
        num = num.replace('(0)','')

    if num.startswith(tuple(code_with62)):
        for code in code_with62:
            if num.startswith(code):
                return '+62' + num.lstrip(code)
    elif num.startswith(tuple(code_no62)):
        for code in code_no62:
            if num.startswith(code):
                return '+62' + num.lstrip('0')
    else:
        return num

def audit(osmfile):
    '''
    Audit and fix the phone numbers.
    Args:
        osmfile: osm file being auditted
    Returns:
        phonenum_types (dict): dictionary updated with new phone numbers
    '''
    osm_file = open(osmfile, "r")
    phonenum_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_phone_num(tag):
                    audit_phonenum_type(phonenum_types, tag.attrib['v'])
                    # update tag.attrib['v'] with the
                    # return from update_phonenum()
                    tag.attrib['v'] = update_phonenum(tag.attrib['v'])

    osm_file.close()
    return phonenum_types

def test():
    phonenum_types = audit(OSMFILE)
    pprint.pprint(dict(phonenum_types))
    for phonenum_type, ways in phonenum_types.iteritems():
        for num in ways:
            better_num = update_phonenum(num)
