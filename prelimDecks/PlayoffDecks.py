
# coding: utf-8

# # Created by Riku Miyao (@YAYtears)

# In[1]:

import csv
from hearthstone.deckstrings import Deck
import json
#Python3 version https://python-pillow.org/
from PIL import Image, ImageDraw, ImageFont


# In[2]:

#https://github.com/HearthSim/Hearthstone-Deck-Tracker/tree/master/Resources/Tiles
tile_url = 'Tiles/'
#Might have to massage the csv file to have valid deck codes for every person
decklists = '2017 HCT Americas Summer Playoffs Decklists.csv'
#https://api.hearthstonejson.com/v1/latest/enUS/cards.collectible.json
cards_json = 'cards.collectible.json'
#stolen from https://deck.codes/ which was probably stolen from Hearthstone or HDT
tile_container_number = 'resources/tile_container_number.png'
tile_container_open = 'resources/tile_container_open.png'
star = 'resources/star.png'

#Where the images are generated, create an empty directory if you are running this the first time
deck_url = 'AM/'
deck_font = 'resources/Ubuntu-B.ttf'
name_font = 'resources/NotoSansCJK-Bold.ttc'


# In[3]:

card_dict = {}
with open(cards_json) as json_file:
    data = json.load(json_file)
    for card in data:
        card_dict[card['dbfId']] = card


# In[4]:

def interpolate_color(minval, maxval, val, color_palette):
    """ Computes intermediate RGB color of a value in the range of minval-maxval
        based on color_palette representing the range. """
    #stack overflow is bae
    max_index = len(color_palette)-1
    v = float(val-minval) / float(maxval-minval) * max_index
    i1, i2 = int(v), min(int(v)+1, max_index)
    (r1, g1, b1, a1), (r2, g2, b2, a2) = color_palette[i1], color_palette[i2]
    f = v - i1
    return int(r1 + f*(r2-r1)), int(g1 + f*(g2-g1)), int(b1 + f*(b2-b1)), int(a1 + f*(a2-a1))


# In[5]:

def find_code(text):
    lines = text.strip().splitlines()
    index = -1
    while lines[index].endswith('Hearthstone.') or not lines[index].strip():
        index-=1
    return lines[index]
def find_code_apac(text):
    lines = text.strip().splitlines()
    index = -1
    while lines[index].startswith('#') or not lines[index].strip():
        index-=1
    return lines[index]
def parse_deck(text):
    try:
        deck = Deck.from_deckstring(text)
    except:
        print(text)
    return deck
def deck_to_image(deck, name):
    hero = card_dict[deck.heroes[0]]
    imclass = Image.open('resources/{}.jpg'.format(hero['playerClass'].lower()))
    cards = [(card_dict[x[0]],x[1]) for x in deck.cards]
    cards.sort(key = lambda x:(x[0]['cost'], x[0]['name']))
    width = 243
    height = 39 * len(cards) + imclass.size[1]
    xoff = 105
    
    master = Image.new('RGBA', (width, height))
    for index, (card, count) in enumerate(cards):
        image = '{}{}.png'.format(tile_url, card['id'])
        im = Image.open(image)
        minx = 105
        maxx = 221
        color_palette = [(41,48,58,255), (93, 68, 68, 0)]
        master.paste(im, (xoff,3+39*index, xoff+130, 39*(index+1)-2))

        gradient = Image.new('RGBA', (width, height))
        draw = ImageDraw.Draw(gradient)
        for x in range(20, minx):
            draw.line([(x, 39*index), (x, 39*(index+1))], fill=color_palette[0])
        for x in range(minx, maxx):
            color = interpolate_color(minx, maxx, x, color_palette)
            draw.line([(x, 39*index), (x, 39*(index+1))], fill=color)
        
        master = Image.alpha_composite(master, gradient)
        draw = ImageDraw.Draw(master)
        font = ImageFont.truetype(deck_font, 15)
        draw.text((39, 10+39*index), card['name'], font=font)
        if count==2:
            bg = Image.open(tile_container_number)
            master.paste(bg, (0,39*index, 239, 39*(index+1)), bg)
            font = ImageFont.truetype(deck_font, 16)
            w, h = draw.textsize('2', font=font)
            draw.text(((30-w)/2+209,(39-h)/2+39*index), '2', font=font, fill=(229, 181, 68))
        elif card['rarity']=='LEGENDARY':
            bg = Image.open(tile_container_number)
            master.paste(bg, (0,39*index, 239, 39*(index+1)), bg)
            imstar = Image.open(star)
            master.paste(imstar, (214, 39*index+10, 233, 39*index+29), imstar)
        else:
            bg = Image.open(tile_container_open)
            master.paste(bg, (0,39*index, 239, 39*(index+1)), bg)
        msg = str(card['cost'])
        w, h = draw.textsize(msg, font=font)
        font = ImageFont.truetype(deck_font, 16)
        draw.text(((34-w)/2, (39-h)/2+39*index), str(card['cost']), font=font)
        #draw.text()
    decklist = master.crop((0,0,243,39*len(cards)))
    master.paste(decklist, (0,97,243,39*len(cards)+97))
    master.paste(imclass, (0,0,243,97))
    font = ImageFont.truetype(name_font, 19)
    w,h = draw.textsize('{} {}'.format(name, hero['playerClass']), font=font)
    draw.text((22, 75-h), '{} {}'.format(name, hero['playerClass'][0]+hero['playerClass'][1:].lower()), font=font)
    return master


# In[6]:

def merge(imgs):
    width = sum(x.size[0] for x in imgs)
    height = max(x.size[1] for x in imgs)
    master = Image.new('RGBA', (width, height))
    x = 0
    for img in imgs:
        w,h = img.size
        master.paste(img, (x, 0, x+w, h), img)
        x+=w
    return master


# In[7]:

def process_EU():
    with open(decklists) as csvfile:
        deckreader = csv.reader(csvfile, delimiter = ',', quotechar='"')
        decks = list(deckreader)
        for row in decks:
            name = row[0]
            deck_imgs = []
            for deck in row[1:]:
                decklist = find_code(deck)
                deck = parse_deck(decklist)
                img = deck_to_image(deck, name)
                deck_imgs.append(img)
            img = merge(deck_imgs)
            img.save('{}{}.jpg'.format(deck_url,name), 'JPEG')


# In[8]:

def process_AP():
    x = []
    with open(decklists) as csvfile:
        deckreader = csv.reader(csvfile, delimiter = ',', quotechar='"')
        decks = list(deckreader)
        for row in decks:
            name = row[0]
            deck_imgs = []
            for deck in row[1:]:
                decklist = find_code_apac(deck)
                if 'imgur' not in decklist:
                    deck = parse_deck(decklist)
                    img = deck_to_image(deck, name)
                    deck_imgs.append(img)
            if len(deck_imgs)>0:
                img = merge(deck_imgs)
                img.save('{}{}.jpg'.format(deck_url,name), 'JPEG')
            x.append(name)
    for a in sorted(x, key=str.upper):
        print(a)


# In[10]:

process_AP()


# In[ ]:



