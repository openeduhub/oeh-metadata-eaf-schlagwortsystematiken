from pathlib import Path
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, SKOS, DCTERMS
from writeFile import writeFile
import shutil
import glob
import os


data_path = "data/comprehensed/"
filename_to_read_ttl = data_path + "eaf-schlagwortsystematiken-all.ttl"
filename_to_save_ttl = data_path + "eaf-schlagwortsystematiken-comprehensed.ttl"

## add translation of topics
replace_dict = {
    "bildende_kunst": "kunst",
    "informationstechnische_bildung": "informatik"
}

## add skip files
skip_files = [
  "elementarbereich",
  "freizeit",
  "fremdsprachen",
  "interkulturelle_bildung",
  "leben",
  "paedagogik",
  "retten",
  "spieldok",
  "sucht",
  "umwelt"
]

try:
  os.remove(Path(filename_to_save_ttl))
  os.remove(Path(filename_to_read_ttl))
except FileNotFoundError:
  pass

Path(filename_to_save_ttl).touch()
Path(filename_to_read_ttl).touch()

with open(filename_to_read_ttl, 'wb') as outfile:
    for filename in Path('data/ttl/').rglob('*.ttl'):
        # skip files from skip_files list
        if os.path.splitext(os.path.basename(filename))[0] in skip_files:
            continue
        with open(filename, 'rb') as readfile:
            shutil.copyfileobj(readfile, outfile)


def parseAllSchoolTopicsGraph():
    OEH = Namespace("http://w3id.org/openeduhub/vocabs/eaf-schlagwortsystematik/")
    base = URIRef(OEH)
    g = Graph()
    g.parse(filename_to_read_ttl, format="ttl")
    title = Literal("EAF-Schlagwortsystematik", lang="de")
    concept_schemes = []

    for s, p, o in g.triples((None, RDF.type, SKOS.ConceptScheme)):
        print(s)

        concept_schemes.append(s)
        g.remove((s, RDF.type, SKOS.ConceptScheme))
        g.add((s, RDF.type, SKOS.Concept))


        # add concept title as prefLabel
        for s, p, obj in g.triples((s, DCTERMS.title, None)):
            # replace titles with discipline vallues
            if obj.value in replace_dict.keys():
                print(f"found {obj.value}, replacing with: {replace_dict[obj.value]} ")
                obj = Literal(replace_dict[obj.value], lang="de")
            print(obj)

            g.add((s, SKOS.prefLabel, obj))

        # change hasTopConcept to narrower
        for s, p, o in g.triples((None, SKOS.hasTopConcept, None)):
            g.add((s, SKOS.narrower, o))
            g.remove((s, SKOS.hasTopConcept, o))

            # remove topConceptOf
            for s, p, o in g.triples((o, SKOS.topConceptOf, None)):
                g.remove((s, SKOS.topConceptOf, o))

        # add to scheme
        g.add((s, SKOS.inScheme, base))

    g.add((base, RDF.type, SKOS.ConceptScheme))
    g.add((base, DCTERMS.title, title))

    for scheme in concept_schemes:
        g.add((base, SKOS.hasTopConcept, scheme))
        g.add((scheme, SKOS.topConceptOf, base))

    for s, p, o in g.triples((None, RDF.type, SKOS.Concept)):
        for s, p, o in g.triples((s, SKOS.inScheme, None)):
            g.remove((s, SKOS.inScheme, o))
        g.add((s, SKOS.inScheme, base))

        # Bind a few prefix, namespace pairs for more readable output
    g.bind("dct", DCTERMS)
    g.bind("skos", SKOS)
    g.bind("oeh", OEH)

    output = g.serialize(format='turtle').decode("utf-8")

    writeFile(filename_to_save_ttl, output)

    print(f"Graph built. File written to: {filename_to_save_ttl}")

parseAllSchoolTopicsGraph()
