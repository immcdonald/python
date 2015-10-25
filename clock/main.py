import os, sys
import argparse
import pygame
from datetime import datetime
from pygame.locals import *

parentPath = os.path.abspath("../common")

if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

from my_log import *
from my_store import *

DEF_TIME_UPDATE_EVENT=(USEREVENT+1)


DEF_SECONDS_IN_A_DAY = (24 * 60 * 60)

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

def time_to_seconds(hour, minute, second):
	return (hour * (60*60)) + (minute * 60) + second

def seconds_to_percent_of_day(seconds, to=2):
	return round(((seconds * 1.0) / (DEF_SECONDS_IN_A_DAY * 1.0)) * 100.00, to)

def time_update(args):
	args.current_time = datetime.now()
	seconds_passed_today = time_to_seconds(args.current_time.hour, args.current_time.minute, args.current_time.second)
	args.day_past_percentage = seconds_to_percent_of_day(seconds_passed_today)

	#sunset = time_to_seconds(18,6,00)
	#sunset_percent =  seconds_to_percent_of_day(sunset)
	#args.log.out(str(sunset_percent)+" --> "+str(args.day_past_percentage))
	pygame.time.set_timer(DEF_TIME_UPDATE_EVENT, 500);


def draw_pixels(screen, offset):
	width, height = screen.get_size()

	counter = (offset % 255);
	for x in range(0, width, 5):
		for y in range(0, height,5):
			screen.set_at((x, y + (counter % 2)), (0, 0, counter))
			counter += 1
			if counter > 255:
				counter = 0

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

	args.day_past_percentage = 0.0;
	args.store = my_store(log=log)

	store_init(args)

	log.set_verbosity(INFO, 0)
	log.set_verbosity(DEBUG, 10)

	run = True

	if pygame.init():
		# Used to manage how fast the screen updates
		clock = pygame.time.Clock()
		pygame.key.set_repeat(1000, 250)

		screen = pygame.display.set_mode((args.width, args.height), pygame.HWSURFACE | pygame.DOUBLEBUF)
 		time_update(args)
 		
 		key_list = []

 		offset = 0
		while(run):
			

			if len(key_list) > 0:
				print key_list

			draw_pixels(screen, offset);
			offset += 1
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					run = False
				elif event.type == DEF_TIME_UPDATE_EVENT:
 					time_update(args)
 				elif event.type == pygame.KEYUP:
					if event.key == K_BACKSPACE:
						pass
					elif event.key == K_TAB:
						pass
					elif event.key == K_CLEAR:
						pass
					elif event.key == K_RETURN:
						pass
					elif event.key == K_PAUSE:
						pass
					elif event.key == K_ESCAPE:
						pass
					elif event.key == K_SPACE:
						pass
					elif event.key == K_EXCLAIM:
						pass
					elif event.key == K_QUOTEDBL:
						pass
					elif event.key == K_HASH:
						pass
					elif event.key == K_DOLLAR:
						pass
					elif event.key == K_AMPERSAND:
						pass
					elif event.key == K_QUOTE:
						pass
					elif event.key == K_LEFTPAREN:
						pass
					elif event.key == K_RIGHTPAREN:
						pass
					elif event.key == K_ASTERISK:
						pass
					elif event.key == K_PLUS:
						pass
					elif event.key == K_COMMA:
						pass
					elif event.key == K_MINUS:
						pass
					elif event.key == K_PERIOD:
						pass
					elif event.key == K_SLASH:
						pass
					elif event.key == K_0:
						pass
					elif event.key == K_1:
						pass
					elif event.key == K_2:
						pass
					elif event.key == K_3:
						pass
					elif event.key == K_4:
						pass
					elif event.key == K_5:
						pass
					elif event.key == K_6:
						pass
					elif event.key == K_7:
						pass
					elif event.key == K_8:
						pass
					elif event.key == K_9:
						pass
					elif event.key == K_COLON:
						pass
					elif event.key == K_SEMICOLON:
						pass
					elif event.key == K_LESS:
						pass
					elif event.key == K_EQUALS:
						pass
					elif event.key == K_GREATER:
						pass
					elif event.key == K_QUESTION:
						pass
					elif event.key == K_AT:
						pass
					elif event.key == K_LEFTBRACKET:
						pass
					elif event.key == K_BACKSLASH:
						pass
					elif event.key == K_RIGHTBRACKET:
						pass
					elif event.key == K_CARET:
						pass
					elif event.key == K_UNDERSCORE:
						pass
					elif event.key == K_BACKQUOTE:
						pass
					elif event.key == K_a:
						pass
					elif event.key == K_b:
						pass
					elif event.key == K_c:
						pass
					elif event.key == K_d:
						pass
					elif event.key == K_e:
						pass
					elif event.key == K_f:
						pass
					elif event.key == K_g:
						pass
					elif event.key == K_h:
						pass
					elif event.key == K_i:
						pass
					elif event.key == K_j:
						pass
					elif event.key == K_k:
						pass
					elif event.key == K_l:
						pass
					elif event.key == K_m:
						pass
					elif event.key == K_n:
						pass
					elif event.key == K_o:
						pass
					elif event.key == K_p:
						pass
					elif event.key == K_q:
						pass
					elif event.key == K_r:
						pass
					elif event.key == K_s:
						pass
					elif event.key == K_t:
						pass
					elif event.key == K_u:
						pass
					elif event.key == K_v:
						pass
					elif event.key == K_w:
						pass
					elif event.key == K_x:
						pass
					elif event.key == K_y:
						pass
					elif event.key == K_z:
						pass
					elif event.key == K_DELETE:
						pass
					elif event.key == K_KP0:
						pass
					elif event.key == K_KP1:
						pass
					elif event.key == K_KP2:
						pass
					elif event.key == K_KP3:
						pass
					elif event.key == K_KP4:
						pass
					elif event.key == K_KP5:
						pass
					elif event.key == K_KP6:
						pass
					elif event.key == K_KP7:
						pass
					elif event.key == K_KP8:
						pass
					elif event.key == K_KP9:
						pass
					elif event.key == K_KP_PERIOD:
						pass
					elif event.key == K_KP_DIVIDE:
						pass
					elif event.key == K_KP_MULTIPLY:
						pass
					elif event.key == K_KP_MINUS:
						pass
					elif event.key == K_KP_PLUS:
						pass
					elif event.key == K_KP_ENTER:
						pass
					elif event.key == K_KP_EQUALS:
						pass
					elif event.key == K_UP:
						pass
					elif event.key == K_DOWN:
						pass
					elif event.key == K_RIGHT:
						pass
					elif event.key == K_LEFT:
						pass
					elif event.key == K_INSERT:
						pass
					elif event.key == K_HOME:
						pass
					elif event.key == K_END:
						pass
					elif event.key == K_PAGEUP:
						pass
					elif event.key == K_PAGEDOWN:
						pass
					elif event.key == K_F1:
						pass
					elif event.key == K_F2:
						pass
					elif event.key == K_F3:
						pass
					elif event.key == K_F4:
						pass
					elif event.key == K_F5:
						pass
					elif event.key == K_F6:
						pass
					elif event.key == K_F7:
						pass
					elif event.key == K_F8:
						pass
					elif event.key == K_F9:
						pass
					elif event.key == K_F10:
						pass
					elif event.key == K_F11:
						pass
					elif event.key == K_F12:
						pass
					elif event.key == K_F13:
						pass
					elif event.key == K_F14:
						pass
					elif event.key == K_F15:
						pass
					elif event.key == K_NUMLOCK:
						args.keyboard_state = args.keyboard_state  & (~KMOD_NUM)
					elif event.key == K_CAPSLOCK:
						args.keyboard_state = args.keyboard_state & (~KMOD_CAPS)
					elif event.key == K_SCROLLOCK:
						pass
					elif event.key == K_RSHIFT:
						args.keyboard_state = args.keyboard_state & (~KMOD_RSHIFT)
					elif event.key == K_LSHIFT:
						args.keyboard_state = args.keyboard_state & (~KMOD_LSHIFT)
					elif event.key == K_RCTRL:
						args.keyboard_state = args.keyboard_state & (~KMOD_RCTRL)
					elif event.key == K_LCTRL:
						args.keyboard_state = args.keyboard_state & (~KMOD_LCTRL)
					elif event.key == K_RALT:
						args.keyboard_state = args.keyboard_state & (~KMOD_RALT)
					elif event.key == K_LALT:
						args.keyboard_state = args.keyboard_state & (~KMOD_LALT)
					elif event.key == K_RMETA:
						args.keyboard_state = args.keyboard_state & (~KMOD_RMETA)					
					elif event.key == K_LMETA:
						args.keyboard_state = args.keyboard_state & (~KMOD_LMETA)
					elif event.key == K_LSUPER:
						pass
					elif event.key == K_RSUPER:
						pass
					elif event.key == K_MODE:
						pass
					elif event.key == K_HELP:
						pass
					elif event.key == K_PRINT:
						pass
					elif event.key == K_SYSREQ:
						pass
					elif event.key == K_BREAK:
						pass
					elif event.key == K_MENU:
						pass
					elif event.key == K_POWER:
						pass
					elif event.key == K_EURO:
						pass
 				elif event.type == pygame.KEYDOWN:
					if event.key == K_BACKSPACE:
						if len(key_list) > 0:
							 del key_list[-1]
					elif event.key == K_TAB:
						pass
					elif event.key == K_CLEAR:
						pass
					elif event.key == K_RETURN:
						dog = "".join(key_list)
						print dog
						key_list = []
					elif event.key == K_PAUSE:
						pass
					elif event.key == K_ESCAPE:
						pass
					elif event.key == K_SPACE:
						key_list.append(' ')
					elif event.key == K_EXCLAIM:
						pass
					elif event.key == K_QUOTEDBL:
						pass
					elif event.key == K_HASH:
						pass
					elif event.key == K_DOLLAR:
						pass
					elif event.key == K_AMPERSAND:
						pass
					elif event.key == K_QUOTE:
						pass
					elif event.key == K_LEFTPAREN:
						pass
					elif event.key == K_RIGHTPAREN:
						pass
					elif event.key == K_ASTERISK:
						pass
					elif event.key == K_PLUS:
						pass
					elif event.key == K_COMMA:
						pass
					elif event.key == K_MINUS:
						pass
					elif event.key == K_PERIOD:
						pass
					elif event.key == K_SLASH:
						pass
					elif event.key == K_0:
						if (args.keyboard_state & KMOD_SHIFT) != 0:
							key_list.append(')')
						else:
							key_list.append('0')
					elif event.key == K_1:
						if (args.keyboard_state & KMOD_SHIFT) != 0:
							key_list.append('!')
						else:
							key_list.append('1')
					elif event.key == K_2:
						if (args.keyboard_state & KMOD_SHIFT) != 0:
							key_list.append('@')
						else:
							key_list.append('2')
					elif event.key == K_3:
						if (args.keyboard_state & KMOD_SHIFT) != 0:
							key_list.append('#')
						else:
							key_list.append('3')
					elif event.key == K_4:
						if (args.keyboard_state & KMOD_SHIFT) != 0:
							key_list.append('$')
						else:
							key_list.append('4')
					elif event.key == K_5:
						if (args.keyboard_state & KMOD_SHIFT) != 0:
							key_list.append('%')
						else:
							key_list.append('5')
					elif event.key == K_6:
						if (args.keyboard_state & KMOD_SHIFT) != 0:
							key_list.append('^')
						else:
							key_list.append('6')
					elif event.key == K_7:
						if (args.keyboard_state & KMOD_SHIFT) != 0:
							key_list.append('&')
						else:
							key_list.append('7')
					elif event.key == K_8:
						if (args.keyboard_state & KMOD_SHIFT) != 0:
							key_list.append('*')
						else:
							key_list.append('8')
					elif event.key == K_9:
						if (args.keyboard_state & KMOD_SHIFT) != 0:
							key_list.append('(')
						else:
							key_list.append('9')
					elif event.key == K_COLON:
						if (args.keyboard_state & KMOD_SHIFT) != 0:
							key_list.append(':')
						else:
							key_list.append(';')
					elif event.key == K_SEMICOLON:
						pass
					elif event.key == K_LESS:
						pass
					elif event.key == K_EQUALS:
						pass
					elif event.key == K_GREATER:
						pass
					elif event.key == K_QUESTION:
						pass
					elif event.key == K_AT:
						pass
					elif event.key == K_LEFTBRACKET:
						pass
					elif event.key == K_BACKSLASH:
						pass
					elif event.key == K_RIGHTBRACKET:
						pass
					elif event.key == K_CARET:
						pass
					elif event.key == K_UNDERSCORE:
						pass
					elif event.key == K_BACKQUOTE:
						pass
					elif ((event.key >= 97) and (event.key <= 172)):
						if ((args.keyboard_state & KMOD_SHIFT) != 0) or ((args.keyboard_state & K_CAPSLOCK) != 0):
							key_list.append(chr(event.key-32))
						else:
							key_list.append(chr(event.key))
					elif event.key == K_DELETE:
						pass
					elif event.key == K_KP0:
						pass
					elif event.key == K_KP1:
						pass
					elif event.key == K_KP2:
						pass
					elif event.key == K_KP3:
						pass
					elif event.key == K_KP4:
						pass
					elif event.key == K_KP5:
						pass
					elif event.key == K_KP6:
						pass
					elif event.key == K_KP7:
						pass
					elif event.key == K_KP8:
						pass
					elif event.key == K_KP9:
						pass
					elif event.key == K_KP_PERIOD:
						pass
					elif event.key == K_KP_DIVIDE:
						pass
					elif event.key == K_KP_MULTIPLY:
						pass
					elif event.key == K_KP_MINUS:
						pass
					elif event.key == K_KP_PLUS:
						pass
					elif event.key == K_KP_ENTER:
						pass
					elif event.key == K_KP_EQUALS:
						pass
					elif event.key == K_UP:
						pass
					elif event.key == K_DOWN:
						pass
					elif event.key == K_RIGHT:
						pass
					elif event.key == K_LEFT:
						pass
					elif event.key == K_INSERT:
						pass
					elif event.key == K_HOME:
						pass
					elif event.key == K_END:
						pass
					elif event.key == K_PAGEUP:
						pass
					elif event.key == K_PAGEDOWN:
						pass
					elif event.key == K_F1:
						pass
					elif event.key == K_F2:
						pass
					elif event.key == K_F3:
						pass
					elif event.key == K_F4:
						pass
					elif event.key == K_F5:
						pass
					elif event.key == K_F6:
						pass
					elif event.key == K_F7:
						pass
					elif event.key == K_F8:
						pass
					elif event.key == K_F9:
						pass
					elif event.key == K_F10:
						pass
					elif event.key == K_F11:
						pass
					elif event.key == K_F12:
						pass
					elif event.key == K_F13:
						pass
					elif event.key == K_F14:
						pass
					elif event.key == K_F15:
						pass
					elif event.key == K_NUMLOCK:
						args.keyboard_state = args.keyboard_state | KMOD_NUM
					elif event.key == K_CAPSLOCK:
						args.keyboard_state = args.keyboard_state | KMOD_CAPS
					elif event.key == K_SCROLLOCK:
						pass
					elif event.key == K_RSHIFT:
						args.keyboard_state = args.keyboard_state | KMOD_RSHIFT
					elif event.key == K_LSHIFT:
						args.keyboard_state = args.keyboard_state | KMOD_LSHIFT
					elif event.key == K_RCTRL:
						args.keyboard_state = args.keyboard_state | KMOD_RCTRL
					elif event.key == K_LCTRL:
						args.keyboard_state = args.keyboard_state | KMOD_LCTRL
					elif event.key == K_RALT:
						args.keyboard_state = args.keyboard_state | KMOD_RALT
					elif event.key == K_LALT:
						args.keyboard_state = args.keyboard_state | KMOD_LALT
					elif event.key == K_RMETA:
						args.keyboard_state = args.keyboard_state | KMOD_RMETA					
					elif event.key == K_LMETA:
						args.keyboard_state = args.keyboard_state | KMOD_LMETA	
					elif event.key == K_LSUPER:
						pass
					elif event.key == K_RSUPER:
						pass
					elif event.key == K_MODE:
						pass
					elif event.key == K_HELP:
						pass
					elif event.key == K_PRINT:
						pass
					elif event.key == K_SYSREQ:
						pass
					elif event.key == K_BREAK:
						pass
					elif event.key == K_MENU:
						pass
					elif event.key == K_POWER:
						pass
					elif event.key == K_EURO:
						pass

 	

 			pygame.display.flip()
			# limit the frame rate
			clock.tick(60)

 	log.out("Good Bye")

if __name__ == "__main__":
	main(sys.argv[1:])
