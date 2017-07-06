'''
This code fixes the street names in OSM file.
The function takes a string with street name as an argument and returns the
fixed name. There are four major types of errors:
1. Inconsistency: abbreviation, capitalization, punctuation
2. Missing the word 'Jalan', Indonesian of 'Street'.
3. Inclusion of city and province names
4. Using English word, 'Road'
Reference: this code was modified from
'Case study: OpenStreetMap Data[SQL] Quiz 10'
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

mapping_street = {  'Jl.': 'Jalan',
                    'Jl': 'Jalan',
                    'Jln': 'Jalan',
                    'Jln.': 'Jalan',
                    'Jl,': 'Jalan',
                    'JL.': 'Jalan',
                    'JLN.': 'Jalan',
                    'jalan': 'Jalan',
                    'JL': 'Jalan',
                    'JALAN': 'Jalan',
                    'Jalan.': 'Jalan'}

def is_street_name(elem):
    '''
    #Check if the element contains a street name.
    '''
    return (elem.attrib['k'] == 'addr:street')

def audit_street_type(street_types, street_name):
    '''
    Classify the types of errors and store in a dictionary.
    '''
    if street_name.split(' ')[0] != 'Jalan':
        if street_name.split(' ')[0] in mapping_street.keys():
            street_types[street_name.split(' ')[0]].add(street_name)
        elif (len(street_name.split(',')) > 1 and
                 street_name.split(',')[1][:4] == ' JL.'):
            street_types['JL._invert'].add(street_name)
        elif street_name.split(' ')[0][:3] == 'Jl.':
            street_types['Jl_no_space'].add(street_name)
        elif len(street_name.split(',')) > 1:
            if street_name.split(',')[0][:5] == 'Jalan':
                street_types['extra'].add(street_name)
            else:
                street_types['extra_no_Jalan'].add(street_name)
        elif street_name[-4:] == 'Road':
            street_types['Road'].add(street_name)
        else:
            street_types['None'].add(street_name)

def update_name(name, mapping_street):
    '''
    Correct the street name based on the type of errors.
    '''
    if name.split(' ')[0] != 'Jalan':
        if name.split(' ')[0] in mapping_street.keys():
            return (name.replace(name.split(' ')[0],
                    mapping_street[name.split(' ')[0]]))
        elif len(name.split(',')) > 1 and name.split(',')[1][:4] == ' JL.':
            name_list = name.split(',')
            return name_list[1].replace(' JL.','Jalan') + ' ' + name_list[0]
        elif name.split(' ')[0][:3] == 'Jl.':
            return name.replace('Jl.','Jalan ')
        elif len(name.split(',')) > 1:
            if name.split(',')[0][:5] == 'Jalan':
                return name.split(',')[0][:-1]
            else:
                return 'Jalan '+ name.split(',')[0][:-1]
        elif name[-4:] == 'Road':
            return 'Jalan '+ name[:-5]
        else:
            return 'Jalan '+ name
    else:
        return name

def audit(osmfile):
    '''
    Audit and fix the street name.
    '''
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
                    # update tag.attrib['v'] with the return from update_name()
                    tag.attrib['v'] = update_name(tag.attrib['v'],
                                                  mapping_street)

    osm_file.close()
    return street_types

def test():
    '''
    Check if the code properly update the street name in a few examples.
    '''
    st_types = audit(OSMFILE)
    pprint.pprint(dict(st_types))
    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping_street)
            if name == "Jln. Danau Poso":
                assert better_name == "Jalan Danau Poso"
            if name == "Jl.Gatot Subroto":
                assert better_name == "Jalan Gatot Subroto"
            if name == "Raya Kerobokan":
                assert better_name == "Jalan Raya Kerobokan"
            if name == "Jalan Bedugul Sidakarya, Denpasar - Bali":
                assert better_name == "Jalan Bedugul Sidakarya"
            if name == "tegalsari 37 pantai berawa ,Canggu":
                print(better_name)
                assert better_name == "Jalan tegalsari 37 pantai berawa"
            if name == "Hanoman Road":
                assert better_name == "Jalan Hanoman"
            if name == "Komplek Burung, JL. Elang":
                assert better_name == "Jalan Elang Komplek Burung"
