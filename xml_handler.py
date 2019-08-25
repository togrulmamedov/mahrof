# module xml_handler.py
# see https://docs.python.org/3.7/library/xml.etree.elementtree.html
# see https://lxml.de/tutorial.html

# import xml.etree.ElementTree as ET
import re

from lxml import etree

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
    paramElement = etree.Element('param')
    paramElement.set('name', name)
    paramElement.text = text

    return paramElement

def insertVendorName(vendorName, text):
    i = 0

    for index, character in enumerate(text):
        if character.isdigit():
            i = index
            break

    if i == 0:
        return None

    return text[:i] + vendorName + ' ' + text[i:]

parser = etree.XMLParser(remove_blank_text=True)
tree = etree.parse('mahrofstore.xml', parser)
root = tree.getroot()
shop = root[0]
currencies = shop[3]
offers = shop[5]

# removing unused currencies
for currency in currencies:
    idParam = currency.get('id', default=None)

    if idParam != 'UAH': currencies.remove(currency)

for offer in offers:
    vendorNameText = offer.find('vendor').text if offer.find('vendor') is not None else 'Ашгабатская Текстильная фабрика'
    vendorCodeText = offer.find('vendorCode').text
    offerNameText = offer.find('name').text
    isLinen = False
    isBathrobe = False
    isSheet = False

    if 'белье' in offerNameText:
        isLinen = True
    elif 'халат' in offerNameText:
        isBathrobe = True
    elif 'простыня' in offerNameText:
        isSheet = True

    # removing unused elements
    removeTag('delivery', offer)
    removeTag('pickup', offer)
    removeTag('sales_notes', offer)
    removeTag('country_of_origin', offer)
    removeTag('vendorCode', offer)

    lastPictureTagIndex = grabLastPictureTagIndex(offer)

    #removing unnecessary text from description
    for description in offer.findall('description'):
        sliceIndex = str(description.text).lower().find('опт/розница')
        description.text = re.sub(r'\n+', ' ', str(description.text)[:sliceIndex].rstrip())
        description.text = '<![CDATA[<p>' + description.text + '</p>]]>'
        reInsert(lastPictureTagIndex + 2, description, offer)

    for vendor in offer.findall('vendor'):
        vendorName = vendor.text
        reInsert(lastPictureTagIndex, vendor, offer)

    stock_quantity = etree.Element('stock_quantity')
    stock_quantity.text = '1'

    offer.insert(lastPictureTagIndex + 1, stock_quantity)

    for name in offer.findall('name'):
        name.text = str(name.text).rstrip().replace("*", "х")
        name.text += ' (' + vendorCodeText + ')'
        textWithVendorName = insertVendorName(vendorNameText, name.text)

        if textWithVendorName is not None:
            name.text = insertVendorName(vendorNameText, name.text)

    dimensions = None
    color = None
    equipment = createParam('Комлпектация', 'Один предмет')
    materialFeatures = None
    material = createParam('Материал', 'Махровые')
    density = None
    decor = None
    purpose = None
    features = None
    manufacturerCountry = createParam('Страна-производитель товара', 'Туркменистан')
    registrationCountry = createParam('Страна регистрации бренда', 'Туркменистан')

    width = None
    length = None

    # linen
    linenSize = None
    duvetCoverWidth = None
    duvetCoverLength = None
    duvetCoverDimensions = None
    linenWidth = None
    linenLength = None
    linenDimensions = None
    linenManufacturer = createParam('Производитель', vendorNameText)
    pillowcaseWidth = None
    pillowcaseLength = None
    pillowcaseSecondWidth = None
    pillowcaseSecondLength = None
    pillowcaseDimensions = None

    # bathrobe
    bathrobeColor = None
    bathrobeLook = None
    bathrobeFeatures = None
    bathrobeFeaturesFilled = False
    bathrobeSex = None
    sleeveLength = None
    bathrobeLength = None

    # removing params
    for param in offer.findall('param'):
        paramName = param.get('name', default=None)

        if paramName is None:
            continue

        if isLinen: # если это белье
            if paramName == 'Тип комплекта':
                if param.text == 'Полуторный':
                    linenSize = createParam('Размер', '1.5-спальный')
                elif param.text == 'Семейный':
                    linenSize = createParam('Размер', 'Семейный')
                elif param.text == 'Двуспальный':
                    linenSize = createParam('Размер', '2-спальный')
                elif param.text == 'Односпальный':
                    linenSize = createParam('Размер', '1-спальный')
                elif param.text == 'Двуспальный Евро':
                    linenSize = createParam('Размер', 'Евро')
            elif paramName == 'Тип ткани':
                material = createParam('Материал', str(param.text).capitalize())
            elif paramName == 'Ширина пододеяльника':
                duvetCoverWidth = param.text
            elif paramName == 'Длина пододеяльника':
                duvetCoverLength = param.text
            elif paramName == 'Ширина простыни':
                linenWidth = param.text
            elif paramName == 'Длина простыни':
                linenLength = param.text
            elif paramName == 'Ширина наволочки':
                pillowcaseWidth = param.text
            elif paramName == 'Длина наволочки':
                pillowcaseLength = param.text
            elif paramName == 'Ширина второй наволочки':
                pillowcaseSecondWidth = param.text
            elif paramName == 'Длина второй наволочки':
                pillowcaseSecondLength = param.text
        elif isBathrobe: # если это халат
            if paramName == 'Цвет':
                bathrobeColor = createParam('Цвет', str(param.text).capitalize().strip())
            elif paramName == 'Тип халата' and param.text == 'Банные':
                bathrobeLook = createParam('Вид', 'Банные')
            elif paramName == 'Наличие капюшона':
                if param.text == 'да':
                    bathrobeFeatures = createParam('Особенности модели', 'С капюшоном')
                elif param.text == 'нет':
                    bathrobeFeatures = createParam('Особенности модели', 'Без капюшона')
                bathrobeFeaturesFilled = True
            elif paramName == 'Наличие карманов' and param.text == 'да' and not bathrobeFeaturesFilled:
                bathrobeFeatures = createParam('Особенности модели', 'С карманами')
                bathrobeFeaturesFilled = True
            elif paramName == 'Наличие пояса' and param.text == 'да' and not bathrobeFeaturesFilled:
                bathrobeFeatures = createParam('Особенности модели', 'С поясом')
                bathrobeFeaturesFilled = True
            elif paramName == 'Пол':
                bathrobeSex = createParam('Пол', str(param.text).capitalize())
            elif paramName == 'Длина рукава':
                if param.text == 'Длинный':
                    sleeveLength = createParam('Длина рукава', 'С длинными рукавами')
                else:
                    sleeveLength = createParam('Длина рукава', 'С короткими рукавами')
            elif paramName == 'Длина халата':
                bathrobeLength = createParam('Длина халата', str(param.text).capitalize())
        else:   # если это полотенце
            if paramName == 'Ширина':
                width = param.text
            elif paramName == 'Длина':
                length = param.text
            elif paramName == 'Цвет':
                color = createParam('Цвет', str(param.text).capitalize())
            elif paramName == 'Плотность':
                density = createParam('Плотность материала', str(round(float(param.text))))
            elif paramName == 'Хлопок':
                materialFeatures = createParam('Особенности материала', '100% хлопок')
            elif paramName == 'Назначение полотенца':
                purpose = createParam('Назначение', str(param.text))
            elif paramName == 'Тематика декора, рисунка':
                decor = createParam('Декорирование', str(param.text).strip().capitalize())
            elif paramName == 'Подарочная упаковка' and param.text == 'да':
                features = createParam('Особенности', 'Подарочные')

        offer.remove(param)

    # appending params
    if isLinen:
        if linenSize is not None: offer.append(linenSize)
        if material is not None: offer.append(material)
        if duvetCoverWidth is not None:
            duvetCoverDimensions = createParam('Размер пододеяльника', str(round(float(duvetCoverWidth))) + 'х' + str(round(float(duvetCoverLength))) + ' см')
            offer.append(duvetCoverDimensions)

        if linenWidth is not None:
            linenDimensions = createParam('Размер простыни', str(round(float(linenWidth))) + 'х' + str(round(float(linenLength))) + ' см')
            offer.append(linenDimensions)

        if pillowcaseWidth is not None:
            if pillowcaseSecondWidth is not None:
                pcFirstWidth = round(float(pillowcaseWidth))
                pcFirstLength = round(float(pillowcaseLength))
                pcSecondWidth = round(float(pillowcaseSecondWidth))
                pcSecondLength = round(float(pillowcaseSecondLength))

                if pcFirstWidth == pcSecondWidth and pcFirstLength == pcSecondLength:
                    pillowcaseDimensions = createParam('Размер наволочки', '2 х ' + str(pcFirstWidth) + 'х' + str(pcFirstLength) + ' см')
                elif pcFirstWidth != pcSecondWidth or pcFirstLength != pcSecondLength:
                    pillowcaseDimensions = createParam('Размер наволочки', str(pcFirstWidth) + 'х' + str(pcFirstLength) + ' см, ' + str(pcSecondWidth) + 'х' + str(pcSecondLength) + ' см')
            else:
                pillowcaseDimensions = createParam('Размер наволочки', str(round(float(pillowcaseWidth))) + 'х' + str(round(float(pillowcaseLength))) + ' см')

            offer.append(pillowcaseDimensions)

        offer.append(linenManufacturer)
    elif isBathrobe:
        offer.append(linenManufacturer)

        if sleeveLength is not None: offer.append(sleeveLength)
        if bathrobeLength is not None: offer.append(bathrobeLength)
        if bathrobeColor is not None: offer.append(bathrobeColor)
        if bathrobeFeatures is not None: offer.append(bathrobeFeatures)

        if bathrobeSex is not None:
            offer.append(bathrobeSex)
        else:
            if 'женский' in offerNameText:
                offer.append(createParam('Пол', 'Женский'))
            elif 'мужской' in offerNameText:
                offer.append(createParam('Пол', 'Мужской'))
            elif 'детский' in offerNameText:
                offer.append(createParam('Пол', 'Детский'))
    else:
        if width is not None:
            dimensions = createParam('Размеры', str(round(float(width))) + 'х' + str(round(float(length))) + ' см')
            offer.append(dimensions)

        if color is not None: offer.append(color)

        offer.append(equipment)

        if materialFeatures is not None: offer.append(materialFeatures)

        offer.append(material)

        if density is not None: offer.append(density)
        if decor is not None: offer.append(decor)
        if purpose is not None: offer.append(purpose)
        if features is not None: offer.append(features)

    offer.append(manufacturerCountry)
    offer.append(registrationCountry)

tree.write('output.xml', encoding='UTF-8', xml_declaration=True, pretty_print=True)


# простыня 113683
# простыня и наволочка 113803