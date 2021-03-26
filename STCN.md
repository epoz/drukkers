# STCN exploration

`2021-03-26`

It's a Friday night, and there have been some crappy things
going on with regards to my passion projects.
What to do? Make something cool, for no rhyme or reason other
than being balm for the soul.

We have the [SPARQL version](https://www.kb.nl/organisatie/onderzoek-expertise/informatie-infrastructuur-diensten-voor-bibliotheken/short-title-catalogue-netherlands-stcn/zoeken-in-de-stcn-met-sparql), but that is slow and makes my head hurt. So time to do some alternative exploring. So first let's just [get a raw data dump](http://data.bibliotheken.nl/doc/dataset/stcn). Downloading the file, `stcn_20201105.ttl` is 542MB of juicy texty triples.

How do we explore an unknown RDF dump, to get at the meat and potatoes? We could [read the manual](https://www.kb.nl/sites/default/files/docs/handleiding_zoeken_in_stcn_met_sparql_versie_011.pdf). On page 10 there is a nice succint example of the kind of triples we can look for. But first let's load the .ttl file into a Python prompt.

Do we convert it to: https://www.rdfhdt.org/ ? No we just use that so we can do another form of querying. Had to trick down [my own Tweet](https://twitter.com/epoz/status/1357679850757255169) where I learned about that in the first place. But it ain't an HDT file yet, so read it raw first with [rdflib](https://rdflib.readthedocs.io/).

```python
from rdflib import Graph

g = Graph()
g.parse("stcn_20201105.ttl", format="ttl")
```

But that is waaaaaay too slow. So we consider [something else](https://github.com/ozekik/lightrdf), to speed things up.

```python
import lightrdf

IRI = "http://data.bibliotheken.nl/id/dataset/stcn"
parser = lightrdf.Parser()
triples = [t for t in parser.parse("./stcn_20201105.ttl", base_iri=IRI)]
```

That gives a hefty 10 541 701 triples. But we can now start exploring:

```python
# First off, what kind of stuff are in there?
>>> set([o for s,p,o in triples if p == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'])
{'http://schema.org/Book',
 'http://schema.org/GovernmentOrganization',
 'http://schema.org/IndividualProduct',
 'http://schema.org/PublicationVolume',
 'http://schema.org/Role',
 'http://xmlns.com/foaf/0.1/Document',
 'https://w3id.org/pnv#PersonName'}

>>> len(set([s for s,p,o in triples if o == 'http://schema.org/Book']))
822949
# That's a lot of books!
# But I would like a list of printer/publisher names
>>> len(set([s for s,p,o in triples if p == 'http://purl.org/dc/elements/1.1/publisher']))
0

# Huh? What's up. Looking at the example in the manual, what are the predicates for a book?
[(s,p,o) for s,p,o in triples if s == 'http://data.kb.nl/catalogus/163434107']
[]

# Empty!
>>> import random
>>> random.choice(triples)
('http://data.bibliotheken.nl/id/nbt/p306666936',
 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
 'http://schema.org/Book')

# Hmmm, other predicates were used. The documentation is out of date.
# Looks like there has been a bit of a clean-up after the first version.
>>> set([p for s,p,o in triples])
{'http://data.bibliotheken.nl/def#bibliographicFormat',
 'http://data.bibliotheken.nl/def#falsifiedAuthor',
 'http://data.bibliotheken.nl/def#hasCollationalFormula',
 'http://data.bibliotheken.nl/def#ppn',
 'http://data.bibliotheken.nl/def#statementOfResponsibilityPart',
 'http://data.bibliotheken.nl/def#stcnFingerprint',
 'http://data.bibliotheken.nl/def#typographicalCharacteristics',
 'http://rdfs.org/ns/void#inDataset',
 'http://schema.org/about',
 'http://schema.org/alternativeTitle',
 'http://schema.org/author',
 'http://schema.org/bookEdition',
 'http://schema.org/contributor',
 'http://schema.org/description',
 'http://schema.org/exampleOfWork',
 'http://schema.org/genre',
 'http://schema.org/hasPart',
 'http://schema.org/holdingArchive',
 'http://schema.org/inLanguage',
 'http://schema.org/isPartOf',
 'http://schema.org/itemLocation',
 'http://schema.org/location',
 'http://schema.org/name',
 'http://schema.org/position',
 'http://schema.org/producer',
 'http://schema.org/publication',
 'http://schema.org/publishedBy',
 'http://schema.org/startDate',
 'http://schema.org/translationOfWork',
 'http://schema.org/volumeNumber',
 'http://semanticweb.cs.vu.nl/2009/11/sem/hasEarliestBeginTimestamp',
 'http://semanticweb.cs.vu.nl/2009/11/sem/hasLatestEndTimestamp',
 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
 'http://www.w3.org/2002/07/owl#sameAs',
 'http://xmlns.com/foaf/0.1/isPrimaryTopicOf',
 'http://xmlns.com/foaf/0.1/primaryTopic',
 'https://w3id.org/pnv#hasName',
 'https://w3id.org/pnv#literalName',
 'https://w3id.org/pnv#nameSpecification'}

 # 🤯 The thlot pickens
# But I STILL want that list of printer/publisher names, please.
>>> publishers = [o for s,p,o in triples if p == 'http://schema.org/publishedBy']
>>> len(publishers)
10926
# That's more like it!

# But, that does not seem to be it either.
len([(s,p,o) for s,p,o in triples if s in publishers])

# What other predicate could it be?
>>> producers = set([o for s,p,o in triples if p == 'http://schema.org/producer']
>>> len(producers)
49976
>>> data = {}
>>> for s,p,o in triples:
>>>    if s in producer:
>>>        data.setdefault(s, {}).setdefault(p, []).append(o)

# Still does not seem to be what I am looking for. 🙁

>>> random.choice(list(data.values()))
{'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': ['http://schema.org/GovernmentOrganization'],
 'http://schema.org/location': ['http://data.bibliotheken.nl/id/thes/p075588749']}
```
