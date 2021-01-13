'''
@note: I'm not attempting to make this code clean or good, just functional
       beacuse this will never be used extensively or have to be re-written.
'''

from PIL import Image, ImageDraw
import json

STEP_SIZE = 16
	
def empty_default_image(im):
	'''
	Set every pixel in the image to have an alpha of zero
	'''
	w,h = im.size

	pixels = []
	for x in range(w):
		for y in range(h):
			pixels.append((0,0,0,0))

	im.putdata(pixels)

def draw_ground_bottom(image, env_tile_set, x0, y0, xt, yt):
	'''
	Loop through top half of ground and put it at the very bottom
	of the iamge to handle special case of extra 8 pixels at the 
	bottom of every mario map
	'''
	step_size = int(STEP_SIZE / 2)

	# we aren't modifying the pixels after the tiles x coordinates
	y0 += STEP_SIZE

	for y in range(step_size):
		for x in range(STEP_SIZE):
			pixel = env_tile_set.getpixel((xt + x, yt + y))
			image.putpixel((x0+x, y0+y), pixel)

def draw_from_sprite_sheet(tile_sets, image, x0, y0, data, tile, is_bottom):
	# ignore air
	if tile == '-':
		return

	if tile not in data: 
		print('Could not parse data for (%i, %i): %s' % (x0, y0, tile))
		return

	tile_data = data[tile]
	tile_set = tile_sets[tile_data['type']]

	# tile set x and y positions
	xt = tile_data['x0']
	yt = tile_data['y0']

	# adjust coodrinates to image space
	x0 *= STEP_SIZE
	y0 *= STEP_SIZE

	# adjust x0 for flag
	if tile == 'flag':
		x0 += 8

	# put pixels into image
	y_step_size = STEP_SIZE
	x_step_size = STEP_SIZE
	if 'extra' in tile_data:
		y_step_size += tile_data['extra']
		y0 -= tile_data['extra']

	if 'reduce_x_right' in tile_data:
		x = tile_data['reduce_x_right']
		x0 += x
		x_step_size -= x
	elif 'reduce_x_left' in tile_data:
		x = tile_data['reduce_x_left']
		xt += x
		x_step_size -=x

	for y in range(y_step_size):
		for x in range(x_step_size):
			pixel = tile_set.getpixel((xt+x, yt+y))
			image.putpixel((x0+x, y0+y), pixel)

	# handle special cases like the 8 pixels at the bottom of the ground
	if is_bottom:
		if tile == '|':
			draw_ground_bottom(image, tile_set, x0, y0, xt, yt)
		elif tile == 'TM' or tile == 'P':
			data = data['P']
			draw_ground_bottom(image, tile_set, x0, y0, data['x0'], data['y0'])

def convert_map(map_str, display_png=True, save_path=None):
	'''
	convert a string of a mario map into an image. 
	- Set save_path to a string for this function to save the image. 
	- Set Display to Falseto not display the map on conversion completion
	'''
	tile_sets = []
	tile_sets.append(Image.open('assets/enemy_tileset.png'))
	tile_sets.append(Image.open('assets/env_tileset.png'))
	tile_sets.append(Image.open('assets/items_objects_tileset.png'))

	f = open('tile_info.json')
	data = json.load(f)['src']
	f.close()

	# this isn't ideal but I'm using old code and I'm not worried about speed
	lvl_map = map_str.strip().split('\n')
	lvl_map = [[lvl_map[j][i] for j in range(len(lvl_map))] for i in range(len(lvl_map[0]))]
	lvl_map = [list(reversed(col)) for col in lvl_map]

	len_column = len(lvl_map)
	len_row = len(lvl_map[0])

	# there are always 8 extra pixels in a mario level
	height = len_row * STEP_SIZE + 8 
	width = len_column * STEP_SIZE

	im = Image.new('RGBA', (width, height))
	empty_default_image(im)

	for x in range(len_column):
		for y in range(len_row):
			tile = lvl_map[x][y]
			draw_from_sprite_sheet(tile_sets, im, x, len_row - y - 1, data, tile, y == 0)

	if display_png:
		im.show()

	if save_path != None and save_path != "":
		im.save(save_path)

if __name__ == '__main__':
	level = 124
	# f = open(f'../mario_web/data/levels/{level}.txt', 'r')
	f = open(f'lvl2.txt', 'r')
	map_text = f.read()
	f.close()

	# convert_map(map_text)
	convert_map(map_text, display_png=False, save_path=f'lvl2.png')