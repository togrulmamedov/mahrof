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

def insertVendorName(venName, text):
    i = 0

    for index, character in enumerate(text):
        if character.isdigit():
            i = index
            break

    if i == 0:
        return None

    return text[:i] + venName + ' ' + text[i:]

def handleName(name, venCodeText, venNameText, col=None):
    name = str(name).rstrip().replace("*", "х")

    if col is None:
        name += ' (' + venCodeText + ')'
    else:
        if col[-2:] == 'ый':
            col = col.replace('ый', 'ое')
        name += ' ' + col + ' (' + venCodeText + ')'

    textWithVendorName = insertVendorName(venNameText, name)

    if textWithVendorName is not None:
        name = insertVendorName(venNameText, name)

    return name

parser = etree.XMLParser(remove_blank_text=True)
tree = etree.parse('mahrofstore.xml', parser)
root = tree.getroot()
shop = root[0]
currencies = shop[3]
categories = shop[4]
offers = shop[5]

# removing unused currencies
for currency in currencies:
    idParam = currency.get('id', default=None)

    if idParam != 'UAH': currencies.remove(currency)

for category in categories:
    category.text = category.text.rstrip().capitalize().replace('*', 'х')
    category.text = " ".join(category.text.split())


for offer in offers:
    vendorNameText = offer.find('vendor').text if offer.find('vendor') is not None else 'Ашгабатская Текстильная фабрика'
    vendorCodeText = offer.find('vendorCode').text
    offerNameText = offer.find('name').text
    isLinen = False
    isBathrobe = False
    isSheet = False
    isPlaid = False

    if 'белье' in offerNameText.lower():
        isLinen = True
    elif 'халат' in offerNameText.lower():
        isBathrobe = True
    elif 'простыня' in offerNameText.lower():
        isSheet = True
    elif 'плед' in offerNameText.lower():
        isPlaid = True

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
        description.text = '<![CDATA[<p>' + description.text + '</p>'
        reInsert(lastPictureTagIndex + 2, description, offer)

    for vendor in offer.findall('vendor'):
        vendorName = vendor.text
        reInsert(lastPictureTagIndex, vendor, offer)

    stock_quantity = etree.Element('stock_quantity')
    stock_quantity.text = '1'

    offer.insert(lastPictureTagIndex + 1, stock_quantity)

    # for name in offer.findall('name'):
    #     name.text = str(name.text).rstrip().replace("*", "х")
    #     name.text += ' (' + vendorCodeText + ')'
    #     textWithVendorName = insertVendorName(vendorNameText, name.text)

    #     if textWithVendorName is not None:
    #         name.text = insertVendorName(vendorNameText, name.text)

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

    # sheet
    sheetWidth = None
    sheetLength = None
    sheetType = createParam('Тип', 'Простыни')
    sheetSort = createParam('Вид', 'Махровые')
    sheetMaterial = createParam('Материал', 'Махра')
    sheetManufacturer = createParam('Производитель', vendorNameText)
    sheetColor = None

    # plaid
    plaidWidth = None
    plaidLength = None
    plaidDecor = None
    plaidComposition = None
    plaidManufacturer = createParam('Производитель', vendorNameText)
    plaidColor = None

    descriptionTail = ''
    # removing params
    for param in offer.findall('param'):
        paramName = param.get('name', default=None)
        paramUnit = param.get('unit', default=None)

        if paramName is None:
            continue

        if paramUnit is None:
            descriptionTail += '<p>' + paramName + ': ' + str(param.text) + '</p><br/>'
        elif paramUnit != '':
            descriptionTail += '<p>' + paramName + ': ' + str(param.text).rstrip() + ' ' + paramUnit + '</p><br/>'

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
        elif isSheet:
            if paramName == 'Цвет':
                sheetColor = createParam('Цвет', str(param.text).rstrip().capitalize())
            elif paramName == 'Ширина простыни':
                sheetWidth = param.text
            elif paramName == 'Длина простыни':
                sheetLength = param.text
        elif isPlaid:
            if paramName == 'Ширина':
                plaidWidth = param.text
            elif paramName == 'Длина':
                plaidLength = param.text
            elif paramName == 'Бахрома' and param.text.lower() == 'есть':
                plaidDecor = createParam('Декорирование', 'Бахрома')
            elif paramName == 'Хлопок':
                plaidComposition = createParam('Состав', 'Хлопок')
            elif paramName == 'Цвет':
                plaidColor = createParam('Цвет', str(param.text).rstrip().capitalize())
        else:   # если это полотенце
            if paramName == 'Ширина':
                width = param.text
            elif paramName == 'Длина':
                length = param.text
            elif paramName == 'Цвет':
                color = createParam('Цвет', str(param.text).rstrip().capitalize())
            elif paramName == 'Плотность':
                density = createParam('Плотность материала', str(round(float(param.text))))
            elif paramName == 'Хлопок':
                materialFeatures = createParam('Особенности материала', '100% хлопок')
            elif paramName == 'Назначение полотенца':
                if str(param.text) == 'Для рук и лица':
                    purpose = createParam('Назначение', 'Для рук')
                else:
                    purpose = createParam('Назначение', str(param.text))
            elif paramName == 'Тематика декора, рисунка':
                if str(param.text).strip().capitalize() == 'Жаккардовая':
                    decor = createParam('Декорирование', 'Жаккард')
                else:
                    decor = createParam('Декорирование', str(param.text).strip().capitalize())
            elif paramName == 'Подарочная упаковка' and param.text == 'да':
                features = createParam('Особенности', 'Подарочные')

        offer.remove(param)

    offer.find('description').text += descriptionTail
    offer.find('description').text = " ".join(offer.find('description').text.split()) + ']]>'

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

        if bathrobeColor is not None:
            offer.append(bathrobeColor)
            offer.find('name').text = handleName(offer.find('name').text, vendorCodeText, vendorNameText, col=bathrobeColor.text)
        else:
            offer.find('name').text = handleName(offer.find('name').text, vendorCodeText, vendorNameText)

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
    elif isSheet:
        if sheetWidth is not None:
            sheetDimensions = createParam('Размеры', str(round(float(sheetWidth))) + 'х' + str(round(float(sheetLength))) + ' см')
            offer.append(sheetDimensions)

        offer.append(sheetType)
        offer.append(sheetSort)
        offer.append(sheetMaterial)
        offer.append(sheetManufacturer)

        if sheetColor is not None:
            offer.append(sheetColor)
            offer.find('name').text = handleName(offer.find('name').text, vendorCodeText, vendorNameText, col=sheetColor.text)
        else:
            offer.find('name').text = handleName(offer.find('name').text, vendorCodeText, vendorNameText)
    elif isPlaid:
        if plaidWidth is not None:
            plaidDimensions = createParam('Размеры', str(round(float(plaidWidth))) + 'х' + str(round(float(plaidLength))) + ' см')
            offer.append(plaidDimensions)

        if plaidDecor is not None: offer.append(plaidDecor)
        if plaidComposition is not None: offer.append(plaidComposition)

        offer.append(plaidManufacturer)

        if plaidColor is not None:
            offer.append(plaidColor)
            offer.find('name').text = handleName(offer.find('name').text, vendorCodeText, vendorNameText, col=plaidColor.text)
        else:
            offer.find('name').text = handleName(offer.find('name').text, vendorCodeText, vendorNameText)
    else:
        if width is not None:
            dimensions = createParam('Размеры', str(round(float(width))) + 'х' + str(round(float(length))) + ' см')
            offer.append(dimensions)

        if color is not None:
            offer.append(color)
            offer.find('name').text = handleName(offer.find('name').text, vendorCodeText, vendorNameText, col=color.text)
        else:
            offer.find('name').text = handleName(offer.find('name').text, vendorCodeText, vendorNameText)

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