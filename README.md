# OpenStreetMap Data Case Study
### Map area
Bali, Indonesia

Data source: [https://www.openstreetmap.org/export#map=10/-8.5342/115.1182](https://www.openstreetmap.org/export#map=10/-8.5342/115.1182)

This dataset is the map of Bali, one of the island of my homecountry, Indonesia. It's my top vacation destination and I am curious to explore the Bali data in OpenStreetMap and opportunites for improvement in the dataset.

### Problems encountered in Bali map dataset
A sample dataset was audited to assess the problems in the Bali dataset. There are several main problems:
* Inconsistent street names, e.g. 'Jalan Pantai Karang', 'Jl. Petitenget', 'Jl Sugirwa', 'Raya Kerobokan', 'Jalan Bedugul Sidakarya, Denpasar - Bali', 'tegalsari 37 pantai berawa ,Canggu', and 'Hanoman Road'.
* Inconsistent country code and phone numbers, e.g. '+62 361 8719334', '0361 765188'.
* Incorrect phone numbers, e.g. '0062286206', '+85 738 481 121', '-8.676387, 115.155813', '1 500 310'.

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
