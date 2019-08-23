# module xml_handler.py

import xml.etree.ElementTree as ET

tree = ET.parse('mahrofstore.xml')
root = tree.getroot()
shop = root[0]
offers = shop[5]

for offer in offers:
    # removing unused elements
    for delivery in offer.findall('delivery'):
        offer.remove(delivery)

    for pickup in offer.findall('pickup'):
        offer.remove(pickup)

    for sales_notes in offer.findall('sales_notes'):
        offer.remove(sales_notes)

tree.write('output.xml', encoding='UTF-8', xml_declaration=True)