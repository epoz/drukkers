# STCN exploration

`2021-03-26`

It's a Friday night.
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

After the initial exploration, back to reading the LOD page at the KB site, I notice the link for `schema:workExample` and follow that to: http://data.bibliotheken.nl/doc/nbt/p192741446

Which gives us a nice overview:

```
<http://data.bibliotheken.nl/id/nbt/p192741446> <http://schema.org/alternateName> "Het vermakelijck landt-leven. Part 3" .
<http://data.bibliotheken.nl/id/nbt/p192741446> <http://data.bibliotheken.nl/def#stcnFingerprint> "168304 - b1 A2 $sic : b2 L3 blij" .
<http://data.bibliotheken.nl/id/nbt/p192741446> <http://schema.org/inLanguage> "iso639-3:dut" .
<http://data.bibliotheken.nl/id/nbt/p192741446> <http://data.bibliotheken.nl/def#typographicalCharacteristics> "illustrations within collation" .
<http://data.bibliotheken.nl/id/nbt/p192741446> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Book> .
<http://data.bibliotheken.nl/id/nbt/p192741446> <http://data.bibliotheken.nl/def#bibliographicFormat> "4°" .
<http://data.bibliotheken.nl/id/nbt/p192741446> <http://schema.org/about> <http://data.bibliotheken.nl/id/thes/p155446258> .
<http://data.bibliotheken.nl/id/nbt/p192741446> <http://data.bibliotheken.nl/def#typographicalCharacteristics> "typeface Gothic" .
<http://data.bibliotheken.nl/id/nbt/p192741446> <http://data.bibliotheken.nl/def#statementOfResponsibilityPart> _:B1d9403b805ce67ad2c15ff827a61be7e .
<http://data.bibliotheken.nl/id/nbt/p192741446> <http://schema.org/about> <http://data.bibliotheken.nl/id/thes/p155446223> .
<http://data.bibliotheken.nl/id/nbt/p192741446> <http://data.bibliotheken.nl/def#hasCollationalFormula> "A-L`SUP`4`LO`" .
<http://data.bibliotheken.nl/id/nbt/p192741446> <http://schema.org/author> _:B3a843468d07ce8109863a99a81a4cdde .
<http://data.bibliotheken.nl/id/nbt/p192741446> <http://data.bibliotheken.nl/def#typographicalCharacteristics> "typographical title page" .
<http://data.bibliotheken.nl/id/nbt/p192741446> <http://schema.org/description> "Includes: Den naerstigen byen-houder, onderrechtende hoe men [...] de byen [...] onderhouden sal; and: De verstandige kock, of Sorghvuldige huyshoudster" .
<http://data.bibliotheken.nl/id/nbt/p192741446> <http://schema.org/name> "De medicyn-winckel, of ervaren huys-houder: zijnde het III. deel van het vermakelyck landt-leven." .
<http://data.bibliotheken.nl/id/nbt/p192741446> <http://xmlns.com/foaf/0.1/isPrimaryTopicOf> _:Bb1767ed6751eff805eda8a2a9b8250a7 .
<http://data.bibliotheken.nl/id/nbt/p192741446> <http://schema.org/publication> _:Bfb9c8a93355c2b54d69472b291ee6851 .
<http://data.bibliotheken.nl/id/nbt/p192741446> <http://data.bibliotheken.nl/def#typographicalCharacteristics> "illustrations on title page" .
_:B1d9403b805ce67ad2c15ff827a61be7e <http://schema.org/position> "1" .
_:B1d9403b805ce67ad2c15ff827a61be7e <http://schema.org/description> "By P. Nyland" .
_:Bfb9c8a93355c2b54d69472b291ee6851 <http://schema.org/publishedBy> <http://data.bibliotheken.nl/id/thes/p075547279> .
_:Bfb9c8a93355c2b54d69472b291ee6851 <http://schema.org/publishedBy> <http://data.bibliotheken.nl/id/thes/p075547244> .
_:Bfb9c8a93355c2b54d69472b291ee6851 <http://schema.org/location> "iso3166-1:NLD" .
_:Bfb9c8a93355c2b54d69472b291ee6851 <http://schema.org/startDate> "1683" .
_:Bfb9c8a93355c2b54d69472b291ee6851 <http://schema.org/description> "Amsterdam, wed. M. de Groot and G. de Groot, 1683" .
_:Bfb9c8a93355c2b54d69472b291ee6851 <http://semanticweb.cs.vu.nl/2009/11/sem/hasEarliestBeginTimestamp> "1683"^^<http://www.w3.org/2001/XMLSchema#gYear> .
_:Bfb9c8a93355c2b54d69472b291ee6851 <http://semanticweb.cs.vu.nl/2009/11/sem/hasLatestEndTimestamp> "1683"^^<http://www.w3.org/2001/XMLSchema#gYear> .
_:B1c592241c859acfda8ee8076a6815393 <https://w3id.org/pnv#literalName> "P. Nyland" .
_:B1c592241c859acfda8ee8076a6815393 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://w3id.org/pnv#PersonName> .
_:Bb1767ed6751eff805eda8a2a9b8250a7 <http://data.bibliotheken.nl/def#ppn> "192741446" .
_:Bb1767ed6751eff805eda8a2a9b8250a7 <http://xmlns.com/foaf/0.1/primaryTopic> <http://data.bibliotheken.nl/id/nbt/p192741446> .
_:Bb1767ed6751eff805eda8a2a9b8250a7 <http://rdfs.org/ns/void#inDataset> <http://data.bibliotheken.nl/id/dataset/stcn> .
_:Bb1767ed6751eff805eda8a2a9b8250a7 <http://www.w3.org/2002/07/owl#sameAs> <http://data.bibliotheken.nl/doc/nbt/p192741446> .
_:Bb1767ed6751eff805eda8a2a9b8250a7 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Document> .
_:B3a843468d07ce8109863a99a81a4cdde <http://schema.org/name> "P. Nyland" .
_:B3a843468d07ce8109863a99a81a4cdde <https://w3id.org/pnv#hasName> _:B1c592241c859acfda8ee8076a6815393 .
_:B3a843468d07ce8109863a99a81a4cdde <http://schema.org/author> <http://data.bibliotheken.nl/id/thes/p070344442> .
_:B3a843468d07ce8109863a99a81a4cdde <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Role> .
```

For which we can then also follow one of the `<http://schema.org/publishedBy>` and then get:

http://data.bibliotheken.nl/doc/thes/p075547279.nt

```
<http://data.bibliotheken.nl/id/thes/p075547279> <http://schema.org/additionalType> <http://www.productontology.org/id/Printer_%28publishing%29> .
<http://data.bibliotheken.nl/id/thes/p075547279> <http://schema.org/name> "Groot, Michiel de (wed.)" .
<http://data.bibliotheken.nl/id/thes/p075547279> <http://schema.org/location> _:Bb0dfdbebfdd115170ae1b4aab504d3b5 .
<http://data.bibliotheken.nl/id/thes/p075547279> <http://schema.org/description> "Amsterdam 1681-1683" .
<http://data.bibliotheken.nl/id/thes/p075547279> <http://xmlns.com/foaf/0.1/isPrimaryTopicOf> _:B66d3431499c0e7eb65befef349af27d1 .
<http://data.bibliotheken.nl/id/thes/p075547279> <http://www.w3.org/2000/01/rdf-schema#label> "Groot, Michiel de (wed.) (Printer)" .
<http://data.bibliotheken.nl/id/thes/p075547279> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Organization> .
_:B66d3431499c0e7eb65befef349af27d1 <http://data.bibliotheken.nl/def#ppn> "075547279" .
_:B66d3431499c0e7eb65befef349af27d1 <http://creativecommons.org/ns#license> <https://creativecommons.org/publicdomain/zero/1.0/> .
_:B66d3431499c0e7eb65befef349af27d1 <http://xmlns.com/foaf/0.1/primaryTopic> <http://data.bibliotheken.nl/id/thes/p075547279> .
_:B66d3431499c0e7eb65befef349af27d1 <http://rdfs.org/ns/void#inDataset> <http://data.bibliotheken.nl/id/dataset/stcn> .
_:B66d3431499c0e7eb65befef349af27d1 <http://www.w3.org/2002/07/owl#sameAs> <http://data.bibliotheken.nl/doc/thes/p075547279> .
_:B66d3431499c0e7eb65befef349af27d1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Document> .
_:Bb0dfdbebfdd115170ae1b4aab504d3b5 <http://schema.org/address> _:B8d1328e57f1a7e0a40e874b6fd406475 .
_:Bb0dfdbebfdd115170ae1b4aab504d3b5 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Place> .
_:B8d1328e57f1a7e0a40e874b6fd406475 <http://schema.org/addressLocality> "Amsterdam" .
_:B8d1328e57f1a7e0a40e874b6fd406475 <http://schema.org/addressCountry> "iso3166-1:NLD" .
_:B8d1328e57f1a7e0a40e874b6fd406475 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/PostalAddress> .
```

But in the original `stcn_20201105.ttl` data dump, there are no subjects for `<http://data.bibliotheken.nl/id/thes/p075547279>` Where are they hiding?

## Eureka

Stop resisting and learn to love the bomb. Just use the SPARQL:

```
SELECT *
WHERE {
?s dc:type "drukker"@nl.
?s skos:prefLabel ?name.
}
```

Running that on the http://openvirtuoso.kbresearch.nl/sparql endpoint, I could dump out a table of printers and their names, as I was looking for. But itn the .ttl dump, there are no dc:type predicates to be found?

Looking at the list of predicates, there is a https://w3id.org/pnv#literalName though, maybe that is a thread to follow.

```python
>>> a = [(s,p,o) for s, p, o in triples if p == 'https://w3id.org/pnv#literalName']
>>> random.choice(a)
('b20867847', 'https://w3id.org/pnv#literalName', '"Petrus Apherdianus"')

# Aha! Now we are getting somewhere
>>> [(s,p,o) for s, p, o in triples if s == 'b20867847']
[('b20867847',
  'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
  'https://w3id.org/pnv#PersonName'),
 ('b20867847', 'https://w3id.org/pnv#literalName', '"Petrus Apherdianus"')]

>>> [(s,p,o) for s, p, o in triples if o == 'b20867847']
[('b20867846', 'https://w3id.org/pnv#hasName', 'b20867847')]

>>> [(s,p,o) for s, p, o in triples if s == 'b20867846']
[('b20867846',
  'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
  'http://schema.org/Role'),
 ('b20867846', 'https://w3id.org/pnv#hasName', 'b20867847'),
 ('b20867846',
  'http://schema.org/contributor',
  'http://data.bibliotheken.nl/id/thes/p072821043'),
 ('b20867846', 'http://schema.org/name', '"Petrus Apherdianus"')]

>>> [(s,p,o) for s, p, o in triples if o == 'b20867846']
[('http://data.bibliotheken.nl/id/nbt/p831161175',
  'http://schema.org/contributor',
  'b20867846')]

>>> [(s,p,o) for s, p, o in triples if s == 'http://data.bibliotheken.nl/id/nbt/p831161175']

[('http://data.bibliotheken.nl/id/nbt/p831161175',
  'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
  'http://schema.org/Book'),
 ('http://data.bibliotheken.nl/id/nbt/p831161175',
  'http://xmlns.com/foaf/0.1/isPrimaryTopicOf',
  'b20867849'),
 ('http://data.bibliotheken.nl/id/nbt/p831161175',
  'http://schema.org/author',
  'b20867844'),
 ('http://data.bibliotheken.nl/id/nbt/p831161175',
  'http://schema.org/description',
  '"TB 242"'),
 ('http://data.bibliotheken.nl/id/nbt/p831161175',
  'http://schema.org/contributor',
  'b20867846'),
 ('http://data.bibliotheken.nl/id/nbt/p831161175',
  'http://schema.org/about',
  'http://data.bibliotheken.nl/id/thes/p155444921'),
 ('http://data.bibliotheken.nl/id/nbt/p831161175',
  'http://schema.org/inLanguage',
  '"iso639-3:lat"'),
 ('http://data.bibliotheken.nl/id/nbt/p831161175',
  'http://schema.org/name',
  '"Loci commvnes, ex similibvs et apophthegmatibvs."'),
 ('http://data.bibliotheken.nl/id/nbt/p831161175',
  'http://schema.org/publication',
  'b20867848'),
 ('http://data.bibliotheken.nl/id/nbt/p831161175',
  'http://schema.org/alternativeTitle',
  '"Works. Selection"'),
 ('http://data.bibliotheken.nl/id/nbt/p831161175',
  'http://data.bibliotheken.nl/def#statementOfResponsibilityPart',
  'b20867843'),
 ('http://data.bibliotheken.nl/id/nbt/p831161175',
  'http://data.bibliotheken.nl/def#statementOfResponsibilityPart',
  'b20867842'),
 ('http://data.bibliotheken.nl/id/nbt/p831161175',
  'http://data.bibliotheken.nl/def#bibliographicFormat',
  '"8°"'),
 ('http://data.bibliotheken.nl/id/nbt/p831161175',
  'http://data.bibliotheken.nl/def#hasCollationalFormula',
  '"A-F`SUP`8`LO` G`SUP`4`LO` H-I`SUP`8`LO`"'),
 ('http://data.bibliotheken.nl/id/nbt/p831161175',
  'http://data.bibliotheken.nl/def#stcnFingerprint',
  '"155708 - b1 A2 itur.$Et : *b2 I4 ros$uia"'),
 ('http://data.bibliotheken.nl/id/nbt/p831161175',
  'http://data.bibliotheken.nl/def#typographicalCharacteristics',
  '"printer\'s device"'),
 ('http://data.bibliotheken.nl/id/nbt/p831161175',
  'http://data.bibliotheken.nl/def#typographicalCharacteristics',
  '"typeface Italic"'),
 ('http://data.bibliotheken.nl/id/nbt/p831161175',
  'http://data.bibliotheken.nl/def#typographicalCharacteristics',
  '"typographical title page"')]
```

Compare the last result above [to the web page](http://data.bibliotheken.nl/doc/nbt/p831161175) at the KB, which is much more readable.

```python
>>> publications = list(set([o for s,p,o in triples if p == 'http://schema.org/publication']))
>>> random.choice(publications)
'b20626606'

>>> [(s,p,o) for s, p, o in triples if s == 'b20626606']
[('b20626606',
  'http://semanticweb.cs.vu.nl/2009/11/sem/hasLatestEndTimestamp',
  '"1748"^^<http://www.w3.org/2001/XMLSchema#gYear>'),
 ('b20626606',
  'http://semanticweb.cs.vu.nl/2009/11/sem/hasEarliestBeginTimestamp',
  '"1748"^^<http://www.w3.org/2001/XMLSchema#gYear>'),
 ('b20626606',
  'http://schema.org/description',
  '"\'sGravenhage, J. Scheltus printer, 1748"'),
 ('b20626606', 'http://schema.org/startDate', '"1748"'),
 ('b20626606', 'http://schema.org/location', '"iso3166-1:NLD"'),
 ('b20626606',
  'http://schema.org/publishedBy',
  'http://data.bibliotheken.nl/id/thes/p075568284')]


>>> len([(s,p,o) for s, p, o in triples if p != 'http://schema.org/publishedBy' and (s == 'http://data.bibliotheken.nl/id/thes/p075568284' or o == 'http://data.bibliotheken.nl/id/thes/p075568284')])
0

# Yes, that's zero.
```

It looks like "Organization" info, or specifically, what I am looking for in the dump the printers info is just not in the raw data dump. But you can access it via the http://data.bibliotheken.nl/ SPARQL query service.
