from os import listdir
from os.path import isfile, join
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import SKOS, DCTERMS
import re
from argparse import ArgumentParser
import uuid

parser = ArgumentParser()
parser.add_argument(
    "-f", "--file", dest="filename", nargs='+',
    help="files to be converted, use '--file fall' to convert all files", metavar="FILE")

args = parser.parse_args()

class Node:
    def __init__(self, _id=None, val=None):
        self.id = _id
        self.value = val
        self.children = []

    def __repr__(self):
        return self.value


def before(value, a):
    re.compile(a)
    # Find first part and return slice before it.
    try:
        pos_a = re.search(a, value).span()[0]
        if pos_a == -1:
            return ""
        return value[0:pos_a]
    except AttributeError:
        return ''

# check if arguments were passed
if len(args.filename) > 0 and "all" not in args.filename:
    files = args.filename
else:
    files = [f for f in listdir('data/txt') if isfile(join('data/txt', f))]

for _file in files:
    print(f'file is {_file}')
    txt = open('data/txt/' + _file).readlines()
    txt_clean = []
    for line in txt:
        line = line.replace('\n', '')
        # TODO also check for tabs
        if line == '':
            continue
        txt_clean.append(line)

    filename = _file.split('.')[0]

    def clean_id(item):
        return item.lower().replace('-', '').replace('(', '').replace(')', '').replace(' ', '_').replace(',', '_').strip()

    def clean_value(item):
        # remove dashes before
        item = item.replace((before(item, "\w")), '')
        # remove tabs after
        item = re.sub("\t", "", item)
        # remove parantheses after word if no paranthese before
        if before(item, "\w") == '' and re.search("\)", item) == None:
            pass
        elif item.count('\(') == item.count('\)'):
            pass
        else:
            item = re.sub("\)", "", item, count=1)
        return item

    data = []
    for i, item in enumerate(txt_clean[1:]):
        d = {}

        d['id'] = str(uuid.uuid4())
        # d['id'] = clean_id(item) + '_id'
        d['value'] = clean_value(item)

        level = item.count('\t')

        if level == 0 and item[:2].count('-') == 0:
            level = 0
        elif level == 0 and item[:2].count('-') == 1:
            level = 1
        elif level == 0 and item[:3].count('-') == 2:
            level = 2
        elif level == 0 and item[:3].count('-') == 3:
            level = 3
        elif level == 1:
            level = 2
        else:
            level += 1

        d['level'] = level
        data.append(d)

    root = Node()

    try:
        for record in data:
            last = root
            for _ in range(record['level']):
                last = last.children[-1]
            last.children.append(Node(record['id'], record['value']))
    except IndexError:
        pass

    name_systematik = filename
    g = Graph()
    n = Namespace(
        "http://w3id.org/openeduhub/vocabs/eaf-schlagwortsystematik/" + name_systematik + "/")

    category = URIRef(n)

    title = Literal(name_systematik, lang="de")
    description = Literal(name_systematik, lang="de")
    creator = Literal("<https://creator.com>")

    # Add triples using store's add method.
    g.add((category, RDF.type, SKOS.ConceptScheme))
    g.add((category, DCTERMS.title, title))
    g.add((category, DCTERMS.description, description))
    g.add((category, DCTERMS.creator, creator))

    # define relevant predicates

    narrower = 'http://www.w3.org/2004/02/skos/core#narrower'
    broader = 'http://www.w3.org/2004/02/skos/core#broader'
    topConceptOf = 'http://www.w3.org/2004/02/skos/core#topConceptOf'

    iteration = 0

    def add_items(root):
        for item in root.children:

            node = n + URIRef(item.id)
            node_prefLabel = Literal(item.value, lang="de")

            g.add((node, RDF.type, SKOS.Concept))
            g.add((node, SKOS.prefLabel, node_prefLabel))
            g.add((node, SKOS.inScheme, category))

            if item.children != []:
                for child in item.children:
                    g.add((node, SKOS.narrower, n + URIRef(child.id)))
                    g.add((n + URIRef(child.id), SKOS.broader, node))

            add_items(item)

    add_items(root)

    for child in root.children:
        node = n + URIRef(child.id)
        g.add((category, SKOS.hasTopConcept, node))
        g.add((node, SKOS.topConceptOf, category))

    # Bind a few prefix, namespace pairs for more readable output
    g.bind("dct", DCTERMS)
    g.bind("skos", SKOS)
    g.bind(name_systematik, category)

    output = g.serialize(format='turtle').decode("utf-8")

    with open('data/ttl/' + filename + '.ttl', 'w') as f:
        f.write(output)
        f.close()
