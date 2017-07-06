import csv, sqlite3

conn = sqlite3.connect('osmproject.sqlite')
cur = conn.cursor()
cur.executescript(
'''
DROP TABLE IF EXISTS Nodes;
DROP TABLE IF EXISTS Nodes_tags;
DROP TABLE IF EXISTS Ways;
DROP TABLE IF EXISTS Ways_tags;
DROP TABLE IF EXISTS Ways_nodes;

CREATE TABLE Nodes (
    id  TEXT NOT NULL PRIMARY KEY UNIQUE,
    lat TEXT,
    lon TEXT,
    user TEXT,
    uid TEXT,
    version TEXT,
    changeset TEXT,
    timestamp TEXT
);

CREATE TABLE Nodes_tags (
    id  TEXT NOT NULL,
    key TEXT,
    value TEXT,
    type TEXT
);

CREATE TABLE Ways (
    id  TEXT NOT NULL PRIMARY KEY UNIQUE,
    user  TEXT,
    uid TEXT,
    version TEXT,
    changeset TEXT,
    timestamp TEXT
);

CREATE TABLE Ways_tags (
    id  INTEGER NOT NULL,
    key TEXT,
    value TEXT,
    type TEXT
);

CREATE TABLE Ways_nodes (
    id  TEXT NOT NULL,
    node_id TEXT NOT NULL,
    position TEXT
);
''')
# Read in the csv file as a dictionary, format the
# data as a list of tuples:
with open('nodes.csv','rb') as nodes_r:
    nodes_dr = csv.DictReader(nodes_r)
    nodes_to_db = [(row['id'],row['lat'],row['lon'],row['user'].decode('utf-8'),
              row['uid'],row['version'],row['changeset'],row['timestamp'])
              for row in nodes_dr]

for idx in range(len(nodes_to_db)):
    cur.execute(
       '''
       INSERT INTO Nodes (id,lat,lon,user,uid,version,changeset,timestamp)
       VALUES (?,?,?,?,?,?,?,?);
       ''',nodes_to_db[idx])
conn.commit()

with open('nodes_tags.csv','rb') as nodes_tags_r:
    nodes_tags_dr = csv.DictReader(nodes_tags_r)
    nodes_tags_to_db = [(row['id'],row['key'],row['value'].decode('utf-8'),
                         row['type']) for row in nodes_tags_dr]

for idx in range(len(nodes_tags_to_db)):
    cur.execute(
       '''
       INSERT INTO Nodes_tags (id,key,value,type)
       VALUES (?,?,?,?);
       ''',nodes_tags_to_db[idx])
conn.commit()

with open('ways.csv','rb') as ways_r:
    ways_dr = csv.DictReader(ways_r)
    ways_to_db = [(row['id'],row['user'].decode('utf-8'),row['uid'],
                   row['version'],row['changeset'],row['timestamp'])
                   for row in ways_dr]

for idx in range(len(ways_to_db)):
    cur.execute(
       '''
       INSERT INTO Ways (id,user,uid,version,changeset,timestamp)
       VALUES (?,?,?,?,?,?);
       ''',ways_to_db[idx])
conn.commit()

with open('ways_tags.csv','rb') as ways_tags_r:
    ways_tags_dr = csv.DictReader(ways_tags_r)
    ways_tags_to_db = [(row['id'],row['key'],row['value'].decode('utf-8'),
                        row['type'])
                        for row in ways_tags_dr]

for idx in range(len(ways_tags_to_db)):
    cur.execute(
       '''
       INSERT INTO Ways_tags (id,key,value,type)
       VALUES (?,?,?,?);
       ''',ways_tags_to_db[idx])
conn.commit()

with open('ways_nodes.csv','rb') as ways_nodes_r:
    ways_nodes_dr = csv.DictReader(ways_nodes_r)
    ways_nodes_to_db = [(row['id'],row['node_id'],row['position'])
                        for row in ways_nodes_dr]

for idx in range(len(ways_nodes_to_db)):
    cur.execute(
       '''
       INSERT INTO Ways_nodes (id,node_id,position)
       VALUES (?,?,?);
       ''',ways_nodes_to_db[idx])
conn.commit()


conn.close()
