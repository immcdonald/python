import os, sys
import argparse
import pygame
import math
from datetime import datetime, timedelta
from pygame.locals import *

parentPath = os.path.abspath("../common")

if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

from my_log import *
from my_store import *

DEF_TIME_UPDATE_EVENT=(USEREVENT+1)
DEF_SECONDS_IN_A_DAY = (24 * 60 * 60)

DEEP_SKY_BLUE=(3,8,39)

def process_key_up(args):
	if args.event.key == K_BACKSPACE:
		pass
	elif args.event.key == K_TAB:
		pass
	elif args.event.key == K_CLEAR:
		pass
	elif args.event.key == K_RETURN:
		pass
	elif args.event.key == K_PAUSE:
		pass
	elif args.event.key == K_ESCAPE:
		pass
	elif args.event.key == K_SPACE:
		pass
	elif args.event.key == K_EXCLAIM:
		pass
	elif args.event.key == K_QUOTEDBL:
		pass
	elif args.event.key == K_HASH:
		pass
	elif args.event.key == K_DOLLAR:
		pass
	elif args.event.key == K_AMPERSAND:
		pass
	elif args.event.key == K_QUOTE:
		pass
	elif args.event.key == K_LEFTPAREN:
		pass
	elif args.event.key == K_RIGHTPAREN:
		pass
	elif args.event.key == K_ASTERISK:
		pass
	elif args.event.key == K_PLUS:
		pass
	elif args.event.key == K_COMMA:
		pass
	elif args.event.key == K_MINUS:
		pass
	elif args.event.key == K_PERIOD:
		pass
	elif args.event.key == K_SLASH:
		pass
	elif args.event.key == K_0:
		pass
	elif args.event.key == K_1:
		pass
	elif args.event.key == K_2:
		pass
	elif args.event.key == K_3:
		pass
	elif args.event.key == K_4:
		pass
	elif args.event.key == K_5:
		pass
	elif args.event.key == K_6:
		pass
	elif args.event.key == K_7:
		pass
	elif args.event.key == K_8:
		pass
	elif args.event.key == K_9:
		pass
	elif args.event.key == K_COLON:
		pass
	elif args.event.key == K_SEMICOLON:
		pass
	elif args.event.key == K_LESS:
		pass
	elif args.event.key == K_EQUALS:
		pass
	elif args.event.key == K_GREATER:
		pass
	elif args.event.key == K_QUESTION:
		pass
	elif args.event.key == K_AT:
		pass
	elif args.event.key == K_LEFTBRACKET:
		pass
	elif args.event.key == K_BACKSLASH:
		pass
	elif args.event.key == K_RIGHTBRACKET:
		pass
	elif args.event.key == K_CARET:
		pass
	elif args.event.key == K_UNDERSCORE:
		pass
	elif args.event.key == K_BACKQUOTE:
		pass
	elif ((args.event.key >= 97) and (args.event.key <= 172)):
		pass
	elif args.event.key == K_DELETE:
		pass
	elif args.event.key == K_KP0:
		pass
	elif args.event.key == K_KP1:
		pass
	elif args.event.key == K_KP2:
		pass
	elif args.event.key == K_KP3:
		pass
	elif args.event.key == K_KP4:
		pass
	elif args.event.key == K_KP5:
		pass
	elif args.event.key == K_KP6:
		pass
	elif args.event.key == K_KP7:
		pass
	elif args.event.key == K_KP8:
		pass
	elif args.event.key == K_KP9:
		pass
	elif args.event.key == K_KP_PERIOD:
		pass
	elif args.event.key == K_KP_DIVIDE:
		pass
	elif args.event.key == K_KP_MULTIPLY:
		pass
	elif args.event.key == K_KP_MINUS:
		pass
	elif args.event.key == K_KP_PLUS:
		pass
	elif args.event.key == K_KP_ENTER:
		pass
	elif args.event.key == K_KP_EQUALS:
		pass
	elif args.event.key == K_UP:
		pass
	elif args.event.key == K_DOWN:
		pass
	elif args.event.key == K_RIGHT:
		pass
	elif args.event.key == K_LEFT:
		pass
	elif args.event.key == K_INSERT:
		pass
	elif args.event.key == K_HOME:
		pass
	elif args.event.key == K_END:
		pass
	elif args.event.key == K_PAGEUP:
		pass
	elif args.event.key == K_PAGEDOWN:
		pass
	elif args.event.key == K_F1:
		pass
	elif args.event.key == K_F2:
		pass
	elif args.event.key == K_F3:
		pass
	elif args.event.key == K_F4:
		pass
	elif args.event.key == K_F5:
		pass
	elif args.event.key == K_F6:
		pass
	elif args.event.key == K_F7:
		pass
	elif args.event.key == K_F8:
		pass
	elif args.event.key == K_F9:
		pass
	elif args.event.key == K_F10:
		pass
	elif args.event.key == K_F11:
		pass
	elif args.event.key == K_F12:
		pass
	elif args.event.key == K_F13:
		pass
	elif args.event.key == K_F14:
		pass
	elif args.event.key == K_F15:
		pass
	elif args.event.key == K_NUMLOCK:
		args.keyboard_state = args.keyboard_state  & (~KMOD_NUM)
	elif args.event.key == K_CAPSLOCK:
		args.keyboard_state = args.keyboard_state & (~KMOD_CAPS)
	elif args.event.key == K_SCROLLOCK:
		pass
	elif args.event.key == K_RSHIFT:
		args.keyboard_state = args.keyboard_state & (~KMOD_RSHIFT)
	elif args.event.key == K_LSHIFT:
		args.keyboard_state = args.keyboard_state & (~KMOD_LSHIFT)
	elif args.event.key == K_RCTRL:
		args.keyboard_state = args.keyboard_state & (~KMOD_RCTRL)
	elif args.event.key == K_LCTRL:
		args.keyboard_state = args.keyboard_state & (~KMOD_LCTRL)
	elif args.event.key == K_RALT:
		args.keyboard_state = args.keyboard_state & (~KMOD_RALT)
	elif args.event.key == K_LALT:
		args.keyboard_state = args.keyboard_state & (~KMOD_LALT)
	elif args.event.key == K_RMETA:
		args.keyboard_state = args.keyboard_state & (~KMOD_RMETA)
	elif args.event.key == K_LMETA:
		args.keyboard_state = args.keyboard_state & (~KMOD_LMETA)
	elif args.event.key == K_LSUPER:
		pass
	elif args.event.key == K_RSUPER:
		pass
	elif args.event.key == K_MODE:
		pass
	elif args.event.key == K_HELP:
		pass
	elif args.event.key == K_PRINT:
		pass
	elif args.event.key == K_SYSREQ:
		pass
	elif args.event.key == K_BREAK:
		pass
	elif args.event.key == K_MENU:
		pass
	elif args.event.key == K_POWER:
		pass
	elif args.event.key == K_EURO:
		pass	

def process_key_down(args):
	if args.event.key == K_BACKSPACE:
		if len(args.key_input_list) > 0:
			 del args.key_input_list[-1]
	elif args.event.key == K_TAB:
		pass
	elif args.event.key == K_CLEAR:
		pass
	elif args.event.key == K_RETURN:
		command_processor(args, "".join(args.key_input_list))
		args.key_input_list = []
	elif args.event.key == K_PAUSE:
		pass
	elif args.event.key == K_ESCAPE:
		pass
	elif args.event.key == K_SPACE:
		args.key_input_list.append(' ')
	elif args.event.key == K_EXCLAIM:
		pass
	elif args.event.key == K_QUOTEDBL:
		pass
	elif args.event.key == K_HASH:
		pass
	elif args.event.key == K_DOLLAR:
		pass
	elif args.event.key == K_AMPERSAND:
		pass
	elif args.event.key == K_QUOTE:
		pass
	elif args.event.key == K_LEFTPAREN:
		pass
	elif args.event.key == K_RIGHTPAREN:
		pass
	elif args.event.key == K_ASTERISK:
		pass
	elif args.event.key == K_PLUS:
		pass
	elif args.event.key == K_COMMA:
		pass
	elif args.event.key == K_MINUS:
		pass
	elif args.event.key == K_PERIOD:
		pass
	elif args.event.key == K_SLASH:
		pass
	elif args.event.key == K_0:
		if (args.keyboard_state & KMOD_SHIFT) != 0:
			args.key_input_list.append(')')
		else:
			args.key_input_list.append('0')
	elif args.event.key == K_1:
		if (args.keyboard_state & KMOD_SHIFT) != 0:
			args.key_input_list.append('!')
		else:
			args.key_input_list.append('1')
	elif args.event.key == K_2:
		if (args.keyboard_state & KMOD_SHIFT) != 0:
			args.key_input_list.append('@')
		else:
			args.key_input_list.append('2')
	elif args.event.key == K_3:
		if (args.keyboard_state & KMOD_SHIFT) != 0:
			args.key_input_list.append('#')
		else:
			args.key_input_list.append('3')
	elif args.event.key == K_4:
		if (args.keyboard_state & KMOD_SHIFT) != 0:
			args.key_input_list.append('$')
		else:
			args.key_input_list.append('4')
	elif args.event.key == K_5:
		if (args.keyboard_state & KMOD_SHIFT) != 0:
			args.key_input_list.append('%')
		else:
			args.key_input_list.append('5')
	elif args.event.key == K_6:
		if (args.keyboard_state & KMOD_SHIFT) != 0:
			args.key_input_list.append('^')
		else:
			args.key_input_list.append('6')
	elif args.event.key == K_7:
		if (args.keyboard_state & KMOD_SHIFT) != 0:
			args.key_input_list.append('&')
		else:
			args.key_input_list.append('7')
	elif args.event.key == K_8:
		if (args.keyboard_state & KMOD_SHIFT) != 0:
			args.key_input_list.append('*')
		else:
			args.key_input_list.append('8')
	elif args.event.key == K_9:
		if (args.keyboard_state & KMOD_SHIFT) != 0:
			args.key_input_list.append('(')
		else:
			args.key_input_list.append('9')
	elif args.event.key == K_COLON:
		if (args.keyboard_state & KMOD_SHIFT) != 0:
			args.key_input_list.append(':')
		else:
			args.key_input_list.append(';')
	elif args.event.key == K_SEMICOLON:
		pass
	elif args.event.key == K_LESS:
		pass
	elif args.event.key == K_EQUALS:
		pass
	elif args.event.key == K_GREATER:
		pass
	elif args.event.key == K_QUESTION:
		pass
	elif args.event.key == K_AT:
		pass
	elif args.event.key == K_LEFTBRACKET:
		pass
	elif args.event.key == K_BACKSLASH:
		pass
	elif args.event.key == K_RIGHTBRACKET:
		pass
	elif args.event.key == K_CARET:
		pass
	elif args.event.key == K_UNDERSCORE:
		pass
	elif args.event.key == K_BACKQUOTE:
		pass
	elif ((args.event.key >= 97) and (args.event.key <= 172)):
		if ((args.keyboard_state & KMOD_SHIFT) != 0) or ((args.keyboard_state & K_CAPSLOCK) != 0):
			args.key_input_list.append(chr(args.event.key-32))
		else:
			args.key_input_list.append(chr(args.event.key))
	elif args.event.key == K_DELETE:
		pass
	elif args.event.key == K_KP0:
		pass
	elif args.event.key == K_KP1:
		pass
	elif args.event.key == K_KP2:
		pass
	elif args.event.key == K_KP3:
		pass
	elif args.event.key == K_KP4:
		pass
	elif args.event.key == K_KP5:
		pass
	elif args.event.key == K_KP6:
		pass
	elif args.event.key == K_KP7:
		pass
	elif args.event.key == K_KP8:
		pass
	elif args.event.key == K_KP9:
		pass
	elif args.event.key == K_KP_PERIOD:
		pass
	elif args.event.key == K_KP_DIVIDE:
		pass
	elif args.event.key == K_KP_MULTIPLY:
		pass
	elif args.event.key == K_KP_MINUS:
		pass
	elif args.event.key == K_KP_PLUS:
		pass
	elif args.event.key == K_KP_ENTER:
		pass
	elif args.event.key == K_KP_EQUALS:
		pass
	elif args.event.key == K_UP:
		pass
	elif args.event.key == K_DOWN:
		pass
	elif args.event.key == K_RIGHT:
		pass
	elif args.event.key == K_LEFT:
		pass
	elif args.event.key == K_INSERT:
		pass
	elif args.event.key == K_HOME:
		pass
	elif args.event.key == K_END:
		pass
	elif args.event.key == K_PAGEUP:
		pass
	elif args.event.key == K_PAGEDOWN:
		pass
	elif args.event.key == K_F1:
		pass
	elif args.event.key == K_F2:
		pass
	elif args.event.key == K_F3:
		pass
	elif args.event.key == K_F4:
		pass
	elif args.event.key == K_F5:
		pass
	elif args.event.key == K_F6:
		pass
	elif args.event.key == K_F7:
		pass
	elif args.event.key == K_F8:
		pass
	elif args.event.key == K_F9:
		pass
	elif args.event.key == K_F10:
		pass
	elif args.event.key == K_F11:
		pass
	elif args.event.key == K_F12:
		pass
	elif args.event.key == K_F13:
		pass
	elif args.event.key == K_F14:
		pass
	elif args.event.key == K_F15:
		pass
	elif args.event.key == K_NUMLOCK:
		args.keyboard_state = args.keyboard_state | KMOD_NUM
	elif args.event.key == K_CAPSLOCK:
		args.keyboard_state = args.keyboard_state | KMOD_CAPS
	elif args.event.key == K_SCROLLOCK:
		pass
	elif args.event.key == K_RSHIFT:
		args.keyboard_state = args.keyboard_state | KMOD_RSHIFT
	elif args.event.key == K_LSHIFT:
		args.keyboard_state = args.keyboard_state | KMOD_LSHIFT
	elif args.event.key == K_RCTRL:
		args.keyboard_state = args.keyboard_state | KMOD_RCTRL
	elif args.event.key == K_LCTRL:
		args.keyboard_state = args.keyboard_state | KMOD_LCTRL
	elif args.event.key == K_RALT:
		args.keyboard_state = args.keyboard_state | KMOD_RALT
	elif args.event.key == K_LALT:
		args.keyboard_state = args.keyboard_state | KMOD_LALT
	elif args.event.key == K_RMETA:
		args.keyboard_state = args.keyboard_state | KMOD_RMETA
	elif args.event.key == K_LMETA:
		args.keyboard_state = args.keyboard_state | KMOD_LMETA
	elif args.event.key == K_LSUPER:
		pass
	elif args.event.key == K_RSUPER:
		pass
	elif args.event.key == K_MODE:
		pass
	elif args.event.key == K_HELP:
		pass
	elif args.event.key == K_PRINT:
		pass
	elif args.event.key == K_SYSREQ:
		pass
	elif args.event.key == K_BREAK:
		pass
	elif args.event.key == K_MENU:
		pass
	elif args.event.key == K_POWER:
		pass
	elif args.event.key == K_EURO:
		pass

def store_init(args):
	args.store.add_store("BLUE", (0,0,255), tuple)
	args.store.add_store("RED", (0,255,0), tuple)
	args.store.add_store("BLUE", (255,0,0), tuple)
	args.store.update_store("RED", (255,0,0), tuple)

def check_negative(value):
    ivalue = int(value)
    if ivalue < 0:
         raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue

def pygame_init(args):
	if pygame.init():
		pygame.mouse.set_visible(false)
	else:
		args.log.out("pygame init has failed.", ERROR)
		return None

def time_to_seconds(miltary_hour, minute, second=0):
	return (miltary_hour * (60*60)) + (minute * 60) + second

def seconds_to_percent_of_day(seconds, to=2):
	return round(((seconds * 1.0) / (DEF_SECONDS_IN_A_DAY * 1.0)) * 100.00, to)

def time_update(args):
	args.current_time = datetime.now()
	args.current_time =	args.current_time - timedelta(seconds=args.debug_time_of_day_offset)

	seconds_passed_today = time_to_seconds(args.current_time.hour, args.current_time.minute, args.current_time.second)
	args.day_past_percentage = seconds_to_percent_of_day(seconds_passed_today)

	#sunset = time_to_seconds(18,6,00)
	#sunset_percent =  seconds_to_percent_of_day(sunset)
	#args.log.out(str(sunset_percent)+" --> "+str(args.day_past_percentage))
	pygame.time.set_timer(DEF_TIME_UPDATE_EVENT, 500);

def command_processor(args, cmd_string):
	print cmd_string

def ellipse_path(args, x, sun_radius=0, horizontal_offset=0,  vertical_offset = 0):	
	x_plane = (args.width-sun_radius) / 2.0
	y_plane = args.height - args.horizon_size - sun_radius

	value = (x-horizontal_offset) ** 2
	
	value = value / ((x_plane**2) * 1.0)
	
	value = 1 - value
	
	value = (y_plane ** 2) * value
	
	value = math.sqrt(value)
	
	value = value + vertical_offset

	return int((args.height-args.horizon_size) - value)

def draw_ellipse_path(args, screen):
	for x in range(1, args.width):
		y = 0
		try:
			y = ellipse_path(args, x-320, sun_radius=6)
		except:
			continue
		screen.set_at((x, y), (255,0,0))	


def draw_sun_from_center(screen, xpos, ypos, color, radius):
	pygame.draw.circle(screen, color, (xpos,ypos), radius, 1)


def render(args, screen):

	# blank the screen
	screen.fill((3,8,39))

	# Draw stuff
	draw_ellipse_path(args, screen)

	# Draw_sun
	if ((args.day_past_percentage >= args.sunrise_percentage) and (args.day_past_percentage <= args.sunset_percentage)):
		delta_percentage = args.day_past_percentage - args.sunrise_percentage
		x_pos = int(args.width * (delta_percentage/100))
		y_pos =  ellipse_path(args, x_pos-(args.width/2), sun_radius=6)
		draw_sun_from_center(screen, x_pos, y_pos, (255,255,255), 6)
		screen.set_at((x_pos, y_pos), (0,255,0))	
		print  args.day_past_percentage, x_pos



	# Draw Horizon
	pygame.draw.rect(screen, (0,0,0), (0, args.height-args.horizon_size, args.width, args.height),0)

	# Draw the Current Time on the screen
	clock_text = args.clock_font_handle.render(args.current_time.strftime("%I:%M:%S %p"), 1, (255, 255, 255))
	textpos = clock_text.get_rect()
	textpos.centerx = args.width / 2;

	textpos.centery = (args.height -(args.horizon_size/2))  
	screen.blit(clock_text, textpos)

	# Draw the fade out if you need too.
	if (args.shade > 0.0) and (args.shade <= 100.00):
		pass

	# Draw text on the screen
	if len(args.key_input_list) > 0:
		text = None
		text = args.font_handle.render("".join(args.key_input_list), 1, (255, 255, 255))
		textpos = text.get_rect()
		textpos.y = args.height - round(args.cmd_font * 0.70,0)
		screen.blit(text, textpos)


	#convert the screen 
	screen.convert()
	pygame.display.flip()


def main(argv):
	log = my_log()
	parser = argparse.ArgumentParser(description='Clock')
	parser.add_argument('-y', "--height", default=400, type=check_negative)
	parser.add_argument('-x', "--width", default=640, type=check_negative)
	parser.add_argument("-v","--verbosity",  nargs='+', help="increase output verbosity")
	args = parser.parse_args(argv)


	log.out("Input Params")
	log.out("============")
	log.out(pformat(vars(args)))


	args.log = log
	args.keyboard_state = KMOD_MODE
	args.cmd_font = 18
	args.shade = 0.00;
	args.clock_font = None
	args.clock_font_size = 70

	args.day_past_percentage = 0.0;
	args.store = my_store(log=log)
	args.key_input_list = []
	args.event = None

	store_init(args)

	log.set_verbosity(INFO, 0)
	log.set_verbosity(DEBUG, 10)

	run = True

	args.sunrise_percentage = seconds_to_percent_of_day(time_to_seconds(6,46,00))
	args.sunset_percentage = seconds_to_percent_of_day(time_to_seconds(16,46,00))


	if pygame.init():
		# Used to manage how fast the screen updates
		clock = pygame.time.Clock()
		
		pygame.key.set_repeat(1000, 250)
		
		args.font_handle = pygame.font.Font(None, args.cmd_font)
		args.clock_font_handle = pygame.font.Font(args.clock_font, args.clock_font_size)
		screen = pygame.display.set_mode((args.width, args.height), pygame.HWSURFACE | pygame.DOUBLEBUF)
 		
		args.debug_time_of_day_offset = 6*(60*60)

 		time_update(args)

 		args.horizon_size = int(args.height * 0.33)

 		args.offset = 0
 		args.x_value = 0


		while(run):
			for args.event in pygame.event.get():
				if args.event.type == pygame.QUIT:
					run = False
				elif args.event.type == DEF_TIME_UPDATE_EVENT:
 					time_update(args)
 				elif args.event.type == pygame.KEYUP:
					process_key_up(args)
 				elif args.event.type == pygame.KEYDOWN:
 					process_key_down(args)

 			render(args, screen)

			# limit the frame rate
			clock.tick(100)


 	#log.out("Good Bye")

if __name__ == "__main__":
	main(sys.argv[1:])
