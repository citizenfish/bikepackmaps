# Overview

This is a list of notes and ideas by Dave in putting together the project. It may make sense at some point to someone. Who knows!

# Map Creation Process

- collate all data into a single OSM file
- ensure that each item in the collated file has a unique id
- design a style file to pick the items you want rendered
- design a typ file to style the rendered items
- use splitter to split the file into tiles
- use mkgmap to create the map

# Collation of data

We are going to use data as follows:-

- a downloaded GB OSM file
- ITT trails
- water points
- bothies
- ncn points (maybe able to do this in OSM)
- supermarkets and shops

The non-OSM data will be curated as a single Geopackage with a layer per type. Each item will have:-

- type
- name

We will then use ogr2osm to convert the geopackage into OSM data 

And finally merge the OSM data together using osmosis

# Rendering a map

I'm going to work backwards and get a map rendering well from a small extract of OSM

This is currently done using the script as follows with the devon-latest.osm.pbf file

```commandline
python build/test_mkgmap.py
```

At the moment the render order of roads does not seem to be right with local roads on top of highways
I'm going to park this and focus on rendering land and sea

At the moment we get a decent result with the Zoomstack style and mapnik.txt as the typ file

