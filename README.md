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
Some statistics about the dataset are provided below.

#### File sizes
```
bali.osm .............. 109.3 MB
osmproject.sqlite ..... 86.2 MB
nodes.csv ............. 41.8 MB
nodes_tags.csv ........ 1.5 MB
ways.csv .............. 4.9 MB
ways_tags.csv ......... 3.8 MB
ways_nodes.csv ........ 14.2 MB
```
#### Number of nodes
```
import sqlite3
conn = sqlite3.connect('osmproject.sqlite')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM Nodes;')
print cur.fetchone()[0]
conn.close()
```
489536

#### Number of ways
```
import sqlite3
conn = sqlite3.connect('osmproject.sqlite')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM Ways;')
print cur.fetchone()[0]
conn.close()
```
79414

#### Number of unique users
```
import sqlite3
conn = sqlite3.connect('osmproject.sqlite')
cur = conn.cursor()
cur.execute('''
SELECT COUNT(DISTINCT(union_node_ways.uid))
FROM (SELECT uid FROM Nodes UNION ALL SELECT uid FROM Ways) as union_node_ways;
''')
print cur.fetchone()[0]
conn.close()
```
1295

#### Top 10 contributing users
```
import sqlite3
conn = sqlite3.connect('osmproject.sqlite')
cur = conn.cursor()
cur.execute('''
SELECT union_node_ways.user, COUNT(*) as num
FROM (SELECT user FROM Nodes UNION ALL SELECT user FROM Ways) as union_node_ways
GROUP BY union_node_ways.user
ORDER BY num DESC
LIMIT 10;
''')
for entry in cur.fetchall():
    print entry[0].decode('utf-8'),entry[1]
conn.close()
```

```
HEN TAM               234502
everyone_sinks_starco 79438
Werner17a             29672
Bernhard Hiller       13752
mahau                 13380
robgeb                12702
wwwFrank              11538
FresRe                8782
Eleonora Easter Henny 8478
osmjessian            8261
```

#### Number of users who have only 1 post
```
import sqlite3
conn = sqlite3.connect('osmproject.sqlite')
cur = conn.cursor()
cur.execute('''
SELECT COUNT(*)
FROM
    (SELECT COUNT(*) as num, union_node_ways.user
     FROM (SELECT user FROM Nodes UNION ALL SELECT user FROM Ways) as union_node_ways
     GROUP BY union_node_ways.user
     HAVING num = 1);
''')
print cur.fetchone()[0]
conn.close()
```
455

The above statistics suggest that there are relatively high number of participants and the entries are not dominated by a few users.

The followings are statistics from further data exploration.

#### Top 10 amenities
```
import sqlite3
conn = sqlite3.connect('osmproject.sqlite')
cur = conn.cursor()
cur.execute('''
SELECT value, COUNT(*) as num
FROM Nodes_tags
WHERE key = 'amenity'
GROUP BY value
ORDER BY num DESC
LIMIT 10;
''')
for entry in cur.fetchall():
    print entry[0].decode('utf-8'),entry[1]
conn.close()
```

```
restaurant        1106
cafe              261
place_of_worship  243
atm               211
bank              167
fuel              111
bar               81
fast_food         79
pharmacy          68
parking           49
```
These statistics match with my experience in Bali.

#### Biggest religion
```
import sqlite3
conn = sqlite3.connect('osmproject.sqlite')
cur = conn.cursor()
cur.execute('''
SELECT Nodes_tags.value, COUNT(*) as num
FROM Nodes_tags
    JOIN (SELECT DISTINCT(id) FROM Nodes_tags WHERE value = 'place_of_worship') as sub
    ON Nodes_tags.id = sub.id
WHERE Nodes_tags.key = 'religion'
GROUP BY Nodes_tags.value
ORDER BY num DESC
LIMIT 1;
''')
for entry in cur.fetchall():
    print entry[0].decode('utf-8'),entry[1]
conn.close()
```
hindu 156

This result is not surprising. Bali is also famous for Hindu spirituality and culture.

#### Most popular cuisines
```
import sqlite3
conn = sqlite3.connect('osmproject.sqlite')
cur = conn.cursor()
cur.execute('''
SELECT Nodes_tags.value, COUNT(*) as num
FROM Nodes_tags
    JOIN (SELECT DISTINCT(id) FROM Nodes_tags WHERE value = 'restaurant') as sub
    ON Nodes_tags.id = sub.id
WHERE Nodes_tags.key = 'cuisine'
GROUP BY Nodes_tags.value
ORDER BY num DESC
LIMIT 15;
''')
for entry in cur.fetchall():
    print entry[0].decode('utf-8'),entry[1]
conn.close()
```

```
regional                  79
indonesian                47
asian                     21
seafood                   17
international             15
italian                   14
chinese                   13
japanese                  13
vegetarian                11
pizza                     7
indonesian;international  6
mexican                   6
thai                      5
indian                    4
noodle                    4
```
These results are also correct. Indonesia has ~17,000 islands and each island has their own culture, food, dialect, etc. When I go to Bali, I always look for the local Bali food and you can find many good Balinese restaurants. There is one catch in the data. Some entries have value = 'indonesian;international'.

#### Most popular shops
```
import sqlite3
conn = sqlite3.connect('osmproject.sqlite')
cur = conn.cursor()
cur.execute('''
SELECT Nodes_tags.value, COUNT(*) as num
FROM Nodes_tags
    JOIN (SELECT DISTINCT(id) FROM Nodes_tags WHERE key = 'name') as sub
    ON Nodes_tags.id = sub.id
WHERE Nodes_tags.key = 'shop'
GROUP BY Nodes_tags.value
ORDER BY num DESC
LIMIT 10;
''')
for entry in cur.fetchall():
    print entry[0].decode('utf-8'),entry[1]
conn.close()
```

```
convenience 161
supermarket 90
clothes 58
bakery 45
massage 45
beauty 36
travel_agency 33
motorcycle 31
electronics 29
yes 27
```
These results also make sense. The interesting part is motorcycle is in the top 10. In Bali, many foreigners come for a long vacation and many of them go around by riding a motorcycle. One catch in the data entries is the value 'yes'. Perhaps, these entries need to be revised.

## Conclusions
Overall, the data provided here agree with my experience in Bali. There are relatively high number of participants and the entries are not dominated by a few users. There are rooms for improvement in consistencies of the street names and phone numbers. In addition, some shop entries with value = 'yes' need to be revised.

## Notes
This code is run in Python 2 to align with Udacity Course. Please setup the environment using openstreetmap.yaml.
To test the codes, please first download the file from [here](https://www.openstreetmap.org/export#map=10/-8.5342/115.1182) and save as 'bali.osm'.
Then, do one of the following two options:
* Run the Jupyter Notebook 'OSM Project Code.ipynb'
* Run `parse_shape_OSM_data_elements.py` as follows
    ```
    from parse_shape_OSM_data_elements import *
    process_map(OSM_PATH, validate=False)
    ```
  followed by running `import_csv_to_sqlite.py` in terminal.
