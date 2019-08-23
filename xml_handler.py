# module xml_handler.py
# see https://docs.python.org/3.7/library/xml.etree.elementtree.html
# see https://lxml.de/tutorial.html

# import xml.etree.ElementTree as ET

from lxml import etree as ET

def removeTag(tagNameStr, parent):
    for tag in parent.findall(tagNameStr):
        parent.remove(tag)

def grabLastPictureTagIndex(parentTag):
    pictureTagsCount = len(parentTag.findall('picture'))

    return (pictureTagsCount + 4)

def reInsert(index, tag, parent):
    parent.remove(tag)
    parent.insert(index, tag)

def createParam(name, text):
    param = ET.Element('param')
    param.set('name', name)
    param.text = text

    return param

parser = ET.XMLParser(remove_blank_text=True)
tree = ET.parse('mahrofstore.xml', parser)
root = tree.getroot()
shop = root[0]
offers = shop[5]

for offer in offers:
    vendorNameText = offer.find('vendor').text if offer.find('vendor') is not None else 'Ашгабатская Текстильная фабрика'
    vendorCodeText = offer.find('vendorCode').text
    offerNameText = offer.find('name').text

    # removing unused elements
    removeTag('delivery', offer)
    removeTag('pickup', offer)
    removeTag('sales_notes', offer)
    removeTag('country_of_origin', offer)
    removeTag('vendorCode', offer)

    lastPictureTagIndex = grabLastPictureTagIndex(offer)

    #removing unnecessary text from description
    for description in offer.findall('description'):
        sliceIndex = str(description.text).find('опт/розница')
        description.text = '<![CDATA[' + str(description.text)[:sliceIndex].rstrip() + ']]>'
        reInsert(lastPictureTagIndex + 2, description, offer)

    for vendor in offer.findall('vendor'):
        vendorName = vendor.text
        reInsert(lastPictureTagIndex, vendor, offer)

    stock_quantity = ET.Element('stock_quantity')
    stock_quantity.text = '1'

    offer.insert(lastPictureTagIndex + 1, stock_quantity)

    dimensions = None
    color = None
    equipment = createParam('Комлпектация', 'Один предмет')
    features = None
    material = createParam('Материал', 'Махровые')
    density = None
    decor = None
    purpose = None
    manufacturerCountry = createParam('Страна-производитель товара', 'Туркменистан')
    registrationCountry = createParam('Страна регистрации бренда', 'Туркменистан')

    width = None
    length = None

    for param in offer.findall('param'):
        paramName = param.get('name', default=None)

        if paramName is None:
            continue

        if paramName == 'Ширина':
            width = param.text
        elif paramName == 'Длина':
            length = param.text
        elif paramName == 'Цвет':
            color = createParam('Цвет', str(param.text).capitalize())
        elif paramName == 'Плотность':
            density = createParam('Плотность материала', str(round(float(param.text))))
        elif paramName == 'Хлопок':
            features = createParam('Особенности материала', '100% хлопок')
        elif paramName == 'Назначение полотенца':
            purpose = createParam('Назначение', str(param.text))
        elif paramName == 'Тематика декора, рисунка':
            decor = createParam('Декорирование', str(param.text).strip().capitalize())

        offer.remove(param)

    if width is not None:
        dimensions = createParam('Размеры', str(round(float(width))) + 'х' + str(round(float(length))) + ' см')
        offer.append(dimensions)

    if color is not None: offer.append(color)

    offer.append(equipment)

    if features is not None: offer.append(features)

    offer.append(material)

    if density is not None: offer.append(density)
    if decor is not None: offer.append(decor)
    if purpose is not None: offer.append(purpose)

    offer.append(manufacturerCountry)
    offer.append(registrationCountry)

tree.write('output.xml', encoding='UTF-8', xml_declaration=True, pretty_print=True)