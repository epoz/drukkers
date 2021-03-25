# Printers and Publishers from the Early Modern Period

## Intro

In 2013 we made a small website called [Geocontexting the printed world](http://arkyves.org/view/geocontext/) focussed on Amsterdam. The site contained a historical map of Amsterdam, which we georeferenced and overlaid on a GoogleMaps view of Amsterdam. The addresses of the printers/publishers were meticulously mapped to longitude/latitude coordinates and shown as clickable items on the map. A histogram on the site allowed the viewer to choose what dates to include, using "start-date" and "end-date" handles. By zooming and and out on the map, and choosing the dates one could intuitively "query" the map, and see what printers were active.

In 2014 we made the [Utrecht version of Geocontexting Printers and Publishers 1450-1800](https://www.arkyves.org/view/geocontextutrecht). This site was similar to the Amsterdam version, with the added feature of being able to view a legend on whether an address for a person was exact or not.

Due to various boring technical and organisational (and mostly embarrassing) reasons, the above two websites are currently slightly broken in various ways.

This repo is a revival and continuation of these projects, and meant to build on these first steps, incorporating the ideas from these projects and building upon them.

## Learning goals

One of the reasons for starting this repo is to learn some new skills. I would like to figure out:

- How Github actions work, so that we can use the repository to drive updates of the system

- If we can use some kind of serverless functions eg. [Google Cloudrun](https://cloud.google.com/run), [Amazon Lambda](https://aws.amazon.com/lambda/) or the brand-new kid on the block: [fly.io](https://fly.io/)

- Using the Google Spreadsheet as a "source of truth" and collaboration hub, while having the data contained therein transformed to Linked Data and user-friendly maps.

- Doing some documentation so others can build on this work, and do similar things.

## Presentations

[DH ECR in Belgium Session 1 2021: GIS](
https://docs.google.com/presentation/d/1GXSaErUDjXm_UGnIWi5VeupWFtuWaxya5vC3Nvxi1GE/edit?usp=sharing)

## Data

Data is being worked on at [this Google drive Spreadsheet](https://docs.google.com/spreadsheets/d/1MMBS0HXemRLqBYbdymyXvv4kxgEfIu6zh7flDMZaCpc/edit?usp=sharing)

And Historical reference of [Utrecht data here](https://docs.google.com/spreadsheets/d/1NEDlEOQfog7lKrzdENmL6go_R5yWUE1vokT8jhhvYss/edit?usp=sharing)

[STCN LOD version](http://data.bibliotheken.nl/doc/dataset/stcn)

## People

The following people have been involved in this project over the years:

Paul Dijstelberge <P.Dijstelberge@uva.nl>

Hans Brandhorst <jpjbrand@xs4all.nl>

Etienne Posthumus <eposthumus@gmail.com>

Marco van Egmond <M.vanEgmond@uu.nl>

## TODO list

- [x] Make basic viewable map using Leaflet/OpenLayers that changes as the spreadsheet is updated.

- [x] Add links to STCN (ISTC later?)

- [ ] Add Metabotnik of printers devices, and link to site

- [ ] Convert and make data available as Linked Data (which vocabs?)

- [ ] Add Antwerp data

- [ ] Convert and add Utrecht data to central spreadsheet

- [ ] Find reference to the Amsterdam historical map used in the original geocontext project

## Links

https://twitter.com/RenskeHoff/status/1350034097054371840
https://dams.antwerpen.be/asset/M2MqqUJAPTtBIiFSQcxqptum
https://search.museumplantinmoretus.be/details/collect/149311
