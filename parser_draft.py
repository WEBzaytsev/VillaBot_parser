import re
import pprint
from facebook_scraper import get_posts
from number_parser import parse as numberparse

GROUPS = [] #ids

LOCATIONS = ['CANGGU', 'SEMINYAK', 'ULUWATU',
             'UBUD', 'JIMBARAN', 'LAVINA', 'SUKAWATI']
MILLION_ABBR = [' mil', ' mill', 'mil', 'mill']

# term
TERMS = ['day', 'month', 'year', 'monthly', 'yearly',
         'daily']
PRICE_REGEX = re.compile(
    r'([0-9]{1,3}[\.,]{0,1}[0-9]{1,3}[\.,]{1}[0-9]{1,3})')  # 400.000.000
# very naive approach - for 1 to 9 digits
PRICE2_REGEX = re.compile(r'([0-9]{1,9})')
NUMBER_REGEX = re.compile(r'\+\d{2,3}[\d -]+')  # +061...
# very naive approach - matches 12 digits
ALTERNATIVE_NUMBER_REGEX = re.compile(r'(\d{12})')
BEDROOM_REGEX = re.compile(r'([0-9])br|([0-9])bed|([0-9])bd')

pp = pprint.PrettyPrinter(indent=4)
posts_texts = []
output_apparts = []


def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)


def parse_text(post):
    appart = {"location": None, "term": None,
              "price": None, "phone": None, "bedrooms": None, "post_url": None}

    # some "preprocess"
    post['text'] = numberparse(post['text'])
    for replacement in MILLION_ABBR:
        text = post['text'].replace(replacement, "000000")
    nowhitespaces = text.replace(" ", "")
    appart["post_url"] = post["post_url"]

    # location
    listinglocation = post['listing_location']
    if not has_numbers(post['listing_location']):
        for location in LOCATIONS:
            if re.search(location, post['listing_location'], re.IGNORECASE):
                appart['location'] = listinglocation
            elif re.search(location, text, re.IGNORECASE):
                appart['location'] = location
    else:
        for location in LOCATIONS:
            if re.search(location, text, re.IGNORECASE):
                appart['location'] = location

    # terms
    # TODO: if on same line with price
    for term in TERMS:
        if re.search(term, text, re.IGNORECASE):
            appart['term'] = term

    # price
    price = PRICE_REGEX.findall(text)
    if price:
        appart['price'] = price[0]
    else:
        appart['price'] = post['listing_price']

    # phone
    phone = NUMBER_REGEX.findall(text)
    phone2 = ALTERNATIVE_NUMBER_REGEX.findall(text)
    if phone:
        appart['phone'] = phone[0]
    elif phone2:
        appart['phone'] = phone2[0]
    if not appart['phone']:
        phone = NUMBER_REGEX.findall(nowhitespaces)
        phone2 = ALTERNATIVE_NUMBER_REGEX.findall(nowhitespaces)
        if phone:
            appart['phone'] = phone[0]
        elif phone2:
            appart['phone'] = phone2[0]

    # bedrooms
    bedrooms = BEDROOM_REGEX.findall(nowhitespaces)
    if bedrooms:
        for x in list(bedrooms[0]):
            if x.isdigit():
                appart['bedrooms'] = x

    return appart


for group in GROUPS:
    for post in get_posts(group, pages=5, cookies='cookies.txt'): #cookies.txt - Netscape HTTP Cookie File
        print(parse_text(post))
