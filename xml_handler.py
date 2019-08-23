# module xml_handler.py
# see https://docs.python.org/3.7/library/xml.etree.elementtree.html

import xml.etree.ElementTree as ET

def removeTag(tagNameStr, parent):
    for tag in parent.findall(tagNameStr):
        parent.remove(tag)

tree = ET.parse('mahrofstore.xml')
root = tree.getroot()
shop = root[0]
offers = shop[5]

for offer in offers:
    # removing unused elements
    removeTag('delivery', offer)
    removeTag('pickup', offer)
    removeTag('sales_notes', offer)

tree.write('output.xml', encoding='UTF-8', xml_declaration=True)