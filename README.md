# OpenStreetMap Data Case Study
### Map area
Bali, Indonesia

Data source: [https://www.openstreetmap.org/export#map=10/-8.5342/115.1182](https://www.openstreetmap.org/export#map=10/-8.5342/115.1182)

This dataset is the map of Bali, one of the island of my homecountry, Indonesia. It's my top vacation destination and I am curious to explore the Bali data in OpenStreetMap and opportunites for improvement in the dataset.

## Problems Encountered in Bali Map Dataset
A sample dataset was audited to assess the problems in the Bali dataset. There are several main problems:
* Inconsistent street names, e.g. 'Jalan Pantai Karang', 'Jl. Petitenget', 'Jl Sugirwa', 'Raya Kerobokan', 'Jalan Bedugul Sidakarya, Denpasar - Bali', 'tegalsari 37 pantai berawa ,Canggu', and 'Hanoman Road'.
* Inconsistent country code and phone numbers, e.g. '+62 361 8719334', '0361 765188'.
* Invalid phone numbers, e.g. '0062286206', '+85 738 481 121', '-8.676387, 115.155813', '1 500 310'.

#### Inconsistent street names
The Indonesian of "street", "road", or "avenue" is "jalan". Unlike in English, we write "Jalan" in front of the street name as adjective comes after noun in Indonesian grammar. "Jalan" can be abbreviated as "Jl.", "JL", "Jl", etc. The dataset contains inconsistent street name with different abbreviation. Furthermore, some street names miss "Jalan" and use English words, e.g. "Road". Here, all of the street names are converted to Indonesian, and all of the prefix are harmonized to "Jalan", e.g. 'Jl. Petitenget' becomes 'Jalan Petitenget' and 'Hanoman Road' becomes 'Jalan Hanoman'. This update is performed by the following `update_name` function.

```
def update_name(name, mapping_street):
    '''
    Correct the street name based on the type of errors.
    '''
    if name.split(' ')[0] != 'Jalan':
        if name.split(' ')[0] in mapping_street.keys():
            return name.replace(name.split(' ')[0],mapping_street[name.split(' ')[0]])
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
```
#### Inconsistent country code in phone numbers
The country code of Indonesia is +62. In order to call landline phones in Bali, we need to dial +62-361-####### where 361 is one of the area codes for Bali. If the phone number is cell phone, we need to dial, for instance, +62-81#-###-####. A lot of the phone numbers start with these codes, while others start with 0361 or 081, which could be used only when called from within Indonesia. To harmonize the phone numbers, all of them are converted to +62-local area code-number format such that 0361 765188 becomes +62361 765188. This update is performed by the following `update_phonenum` function.
```
def update_phonenum(num):
    '''
    Fix the phone numbers based on the type of errors.
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
```
#### Invalid phone numbers
While exploring inconsistency of the phone numbers, I found 5 invalid phone numbers:
* -8.676387, 115.155813
* 1 500 310
* +85 738 481 121
* 07245465
* +79684349570

The function `is_phone_num` below checks the validity of the phone numbers and ignore all invalid phone numbers.
```
def is_phone_num(elem):
    '''
    Check if the element contains phone number.
    '''    
    if elem.attrib['k'] == "phone":
        if not elem.attrib['v'].startswith(tuple(codes)):
            print('Incorrect phone numbers:',elem.attrib['v'])

    return (elem.attrib['k'] == "phone" and
            elem.attrib['v'].startswith(tuple(codes)))
```
## Data Overview and Additional Exploration

#### File sizes
Some statistics about the dataset are provided below.
```
bali.osm .............. 109.3 MB
osmproject.sqlite ..... 86.2 MB
nodes.csv ............. 41.8 MB
nodes_tags.csv ........ 1.5 MB
ways.csv .............. 4.9 MB
ways_tags.csv ......... 3.8 MB
ways_nodes.csv ........ 14.2 MB
```
