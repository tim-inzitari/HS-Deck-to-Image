from PIL import Image, ImageDraw, ImageFont
import json
import io
import os

tile_loc = 'hs-card-tiles/Tiles/'
tile_dest = 'Tiles'
hero_dest = 'Heros'
deck_font = 'resources/Belwe-Bold.ttf'
name_font = 'resources/NotoSansCJK-Bold.ttc'
star = 'resources/star.png'

# https://api.hearthstonejson.com/v1/latest/enUS/cards.collectible.json 
cards_json = 'resources/cards.collectible.json'
tile_legend = 'resources/frame_legendary.png'
tile_epic = 'resources/frame_epic.png'
tile_rare = 'resources/frame_rare.png'
tile_common = 'resources/frame_common.png'

card_dict = {}
with open(cards_json, encoding="utf-8") as json_file:
    data = json.load(json_file)
    for card in data:
        card_dict[card['id']] = card

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

def draw_shadow(draw,x,y,text,font,shadowcolor="black"):
    # thin border
    draw.text((x-1, y-1), text, font=font, fill=shadowcolor)
    draw.text((x+1, y+1), text, font=font, fill=shadowcolor)
    draw.text((x+1, y-1), text, font=font, fill=shadowcolor)
    draw.text((x-1, y+1), text, font=font, fill=shadowcolor)

def process(cardid):
    card = card_dict[cardid]
    if 'cost' not in card:
        process_hero(card)
        return
    width = 243
    xoff = 105
    height = 39
    minx = 105
    maxx = 221
    color_palette = [(41,48,58,255), (93, 68, 68, 0)]

    image = '{}{}.png'.format(tile_loc, card['id'])
    im = Image.open(image)
    master = Image.new('RGBA', (width, height))
    master.paste(im, (xoff,3, xoff+130, 37))
    gradient = Image.new('RGBA', (width, height))
    draw = ImageDraw.Draw(gradient)
    draw.rectangle([(20, 0), (minx, 39)], fill=color_palette[0])
    for x in range(minx, maxx):
        color = interpolate_color(minx, maxx, x, color_palette)
        draw.line([(x,0), (x,39)], fill=color)
    master = Image.alpha_composite(master, gradient)
    draw = ImageDraw.Draw(master)
    font = ImageFont.truetype(deck_font, 15)

    def writeCost(font):
        msg = str(card['cost'])
        w, h = draw.textsize(msg, font=font)
        font = ImageFont.truetype(deck_font, 18)
        draw_shadow(draw,(44-w)/2,(39-h)/2-1,str(card['cost']), font)
        draw.text(((44-w)/2, (39-h)/2-1), str(card['cost']), font=font)
    
    draw_shadow(draw, 45, 13, card['name'], font)
    draw.text((45, 13), card['name'], font=font)
    if card['rarity']=='LEGENDARY':
        bg = Image.open(tile_legendary)
        master.paste(bg, (0, 0, 239, 39), bg)
        imstar = Image.open(star)
        master.paste(imstar, (214, 10, 233, 29), imstar)

        writeCost(font)

        master.save(u'{}/{}.png'.format(tile_dest,cardid), 'PNG')
    else:
        if card['rarity'] == 'EPIC':
            bg = Image.open(tile_epic)
        if card['rarity'] == 'RARE':
            bg = Image.open(tile_rare)
        if card['rarity'] == 'COMMON':
            bg = Image.open(tile_common)
       
        master.paste(bg, (0, 0, 239, 39), bg)

        writeCost(font)

        master.save(u'{}/{}.png'.format(tile_dest,cardid), 'PNG')

        if card['rarity'] == 'EPIC':
            bg = Image.open(tile_epic)
        if card['rarity'] == 'RARE':
            bg = Image.open(tile_rare)
        if card['rarity'] == 'COMMON':
            bg = Image.open(tile_common)

        master.paste(bg, (0, 0, 239, 39), bg)
        font = ImageFont.truetype(deck_font, 16)
        w, h = draw.textsize('2', font=font)
        draw.text(((30-w)/2+209,(39-h)/2), '2', font=font, fill=(229, 181, 68))

        writeCost(font)

        master.save(u'{}/{}_2.png'.format(tile_dest,cardid), 'PNG')

def process_hero(card):
    if card['set'] != 'CORE':
        return
    title = card['cardClass'][0].upper()+card['cardClass'][1:].lower()+' Deck'
    imclass = Image.open('resources/{}.jpg'.format(card['cardClass'].lower()))
    draw = ImageDraw.Draw(imclass)
    font = ImageFont.truetype(name_font, 19)
    w,h = draw.textsize(title, font=font)
    draw_shadow(draw, 22, 75-h, title, font)
    draw.text((22, 75-h), title, font=font)
    imclass.save('{}/{}.jpg'.format(hero_dest, card['cardClass'].lower()))
    onetwothree = ['Primary', 'Secondary', 'Tertiary']
    for i in range(3):
        title = onetwothree[i]+' Deck'
        imclass = Image.open('resources/{}.jpg'.format(card['cardClass'].lower()))
        draw = ImageDraw.Draw(imclass)
        font = ImageFont.truetype(name_font, 19)
        w,h = draw.textsize(title, font=font)
        draw_shadow(draw, 22, 75-h, title, font)
        draw.text((22, 75-h), title, font=font)
        imclass.save('{}/{}_{}.jpg'.format(hero_dest, card['cardClass'].lower(), i+1))

if not os.path.exists(tile_dest):
    os.mkdir(tile_dest)
if not os.path.exists(hero_dest):
    os.mkdir(hero_dest)
for card in card_dict:
    process(card)
