# -*- coding: utf-8 -*-
"""
Created on Sun Oct  4 21:42:01 2015

@author: nannapan
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
"""
The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function with the element
as an argument. You should return a dictionary, containing the shaped data for that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB. 

Note that in this exercise we do not use the 'update street name' procedures
you worked on in the previous exercise. If you are using this code in your final
project, you are strongly encouraged to use the code from previous exercise to 
update the street names before you save them to JSON. 


<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]


<tag k="natural" v="water"/>
<tag k="wikipedia" v="en:Hussain Sagar"/>
<tag k="locality" v="Banjara Hills"/>
<tag k="railway" v="rail"/>
<tag k="electrified" v="contact_line"/>
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

def shape_way(element):
    lis= [ ]
    node={}
    node['id']=element.attrib['id']
    node['type']=element.tag
    if 'user' in element.attrib.keys():
        node['user']=element.attrib['user']   
    other_attrib=['name','oneway','source','highway','ref','lanes','surface','maxspeed','bicycle','bridge']    
    for child in element:
        if 'ref' in child.attrib.keys():
            lis.append( child.attrib['ref'])
        if 'k' in child.attrib.keys() and child.attrib['k'] in other_attrib:
            node[child.attrib['k']]=child.attrib['v'];
    if(len(lis)>0):        
        node['node_refs']=lis
    
    return node   

def shape_node(element):
    node={}
    node['id']=element.attrib['id']
    node['type']=element.tag
    if 'visible' in element.attrib.keys():
        node['visible']=element.attrib['visible']
    else:
        node['visible']=None
    dic={}
    for a in CREATED:
        dic[a]=element.attrib[a]
    node['created']=dic
    pos=[ ]
    if 'lat' in element.attrib.keys():  
        pos.append(float(element.attrib['lat']))
    else:
        pos.append("None")
    if 'lon' in element.attrib.keys():
        pos.append(float(element.attrib['lon']))
    else:
        pos.append("None")
    node['pos']=pos

    dic={}
    location_arrtib=['addr:street','addr:housenumber','addr:city','addr:postcode']
    other_attrib=['tourism','shelter','amenity','cuisine','name','phone','place','created_by','highway','religion','building']
    for child in element:
        if 'k' in child.attrib.keys():
            if(child.attrib['k'] in location_arrtib):
                t=child.attrib['k'].split(':')
                if(t[1]=="postcode") and len(child.attrib['v'][-6:])==6 and any (c.isalpha() for c in child.attrib['v'][-6:])==False:
                    child.attrib['v']=child.attrib['v'][-6:]
                dic[t[1]]=child.attrib['v']
            if (child.attrib['k'] in other_attrib):
                node[child.attrib['k']]=child.attrib['v']
                    
    if(len(dic)>0):
        node['address']=dic        
    return node    
     

def shape_element(element):
    if element.tag == "node":
        return shape_node(element)
    elif element.tag=="way":
        return shape_way(element)
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map('hyderabad_india.osm', True) #specific file name
    #pprint.pprint(data)
    
    print (data[0])
    
if __name__ == "__main__":
    test()
