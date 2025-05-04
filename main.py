import json
import xml.etree.ElementTree as ET
from lxml import etree
import os
from pathlib import Path
from xml.dom import minidom

folder_name = "out"
folder_path = Path('.') / folder_name
folder_path.mkdir(exist_ok=True)

tree = ET.parse("test_input.xml")
root = tree.getroot()

storage_class = {}
storage_agr = []
start = ""

for child in root:
    if child.tag == "Class":
        class_name = child.get('name')
        if child.get('isRoot', '') == 'true':
            start = str(child.get('name'))
            storage_class[class_name] = {
                "class": class_name,
                "isRoot": bool(1), 
                "documentation": child.get('documentation'),
                "parameters": [x.attrib for x in child.findall('Attribute') ]
            }
        else:
            storage_class[class_name] = {
                "class": class_name,
                "isRoot": bool(0), 
                "documentation": child.get('documentation'),
                "max": "1",
                "min": "0",
                "parameters": [x.attrib for x in child.findall('Attribute') ]
            }
       
    elif child.tag == "Aggregation":
        source = child.get('source')
        target = child.get('target')
        multiplicity = child.get('targetMultiplicity')
        max_value = max(str(child.get('sourceMultiplicity')).split('..') if '..' in str(child.get('sourceMultiplicity')) else str(child.get('sourceMultiplicity')))
        min_value = min(str(child.get('sourceMultiplicity')).split('..') if '..' in str(child.get('sourceMultiplicity')) else str(child.get('sourceMultiplicity')))
        storage_agr.append([source,target,multiplicity,max_value,min_value])
        storage_class[str(source)]['min'] = min_value
        storage_class[str(source)]['max'] = max_value
        storage_class[str(target)]['parameters'].append({
            "name": source,
            "type": 'class'
        })
        
final_json = json.dumps([storage_class[x] for x in storage_class], indent=4, separators=(", ", ": "))

with open(os.path.join(folder_path, "meta.json"), "a") as f:
    f.write(final_json)

def making_xml(fin, s, stor):
    if stor[s]['parameters'] == []:
        fin.text = " "
    for item in stor[s]['parameters']:
        if list(item.values())[1] != 'class':
            s_elem = ET.SubElement(fin, list(item.values())[0])
            s_elem.text = list(item.values())[1]
        else:
            break
    for item in stor[s]['parameters']:
        if list(item.values())[1] == 'class':
            s_elem = ET.SubElement(fin, list(item.values())[0])
            making_xml(s_elem, list(item.values())[0], stor)

final_xml = ET.Element(start)
making_xml(final_xml, start, storage_class)
ET.indent(final_xml, space="    ", level=0)

with open(os.path.join(folder_path, "config.xml"), "wb") as f:
    f.write(ET.tostring(final_xml, "utf-8"))

