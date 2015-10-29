import os, sys
import argparse
import pygame
import math
from datetime import datetime
from pygame.locals import *

parentPath = os.path.abspath("../common")

if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

from my_log import *
from my_store import *

DEF_TIME_UPDATE_EVENT=(USEREVENT+1)
DEF_SECONDS_IN_A_DAY = (24 * 60 * 60)




def command_processor(args, cmd_string):
	print cmd_string


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

def draw_sky(args, screen):
	pass

def cal_local_standard_time_meridian(local_delta_from_gmt):
	degrees = 15
	return degrees * local_delta_from_gmt 

def convert_deg_min_sec_2_dec(args, deg, minutes, seconds, direction):
	valid_directions_type = ['N', 'S', 'E', 'W']

	if direction.upper() in valid_directions_type:
		multiplier = 1
		if direction.upper() == "S" or direction.upper() == "W":
			multiplier = -1
		return (deg + (minutes/60.0) + (seconds/3600.00)) * multiplier
	else:
		args.log.out("% is not a valid direction" % direction, ERROR)
		return None


def decimalDegrees2DMS(value,type):
    """
        Converts a Decimal Degree Value into
        Degrees Minute Seconds Notation.
        
        Pass value as double
        type = {Latitude or Longitude} as string
        
        returns a string as D:M:S:Direction
        created by: anothergisblog.blogspot.com 
    """
    degrees = int(value)
    submin = abs( (value - int(value) ) * 60)
    minutes = int(submin)
    subseconds = abs((submin-int(submin)) * 60)

    direction = ""
    if type == "long":
        if degrees < 0:
            direction = "W"
        elif degrees > 0:
            direction = "E"
        else:
            direction = ""
    elif type == "lat":
        if degrees < 0:
            direction = "S"
        elif degrees > 0:
            direction = "N"
        else:
            direction = "" 
    notation = [degrees, minutes, subseconds, direction]
    return notation

def cal_equation_of_time(days_since_start_of_year):

	print "Day:", days_since_start_of_year
	print (360.00/365.00)
	print (days_since_start_of_year-81)


	B = (360.00/365.00) * (days_since_start_of_year-81)
	print "B:", B
	eot = (9.87 * math.sin(2*B)) - (7.53 * math.cos(B)) - (1.5 * math.sin(B))
	print "EOT:", eot

def calculate_fractional_year_in_degrees(days_since_start_of_year, military_hour, minutes):
	return (360.0 / 365.25) * (days_since_start_of_year + ((military_hour + (minutes/60.0))/24.0))

def calculate_sun_declination(fractional_year_in_degrees):
	return 0.396372-(22.91327*math.cos(fractional_year_in_degrees)) + (4.02543*math.sin(fractional_year_in_degrees))-(0.387205*math.cos(2*fractional_year_in_degrees))+ (0.051967*math.sin(2*fractional_year_in_degrees))- (0.154527*math.cos(3*fractional_year_in_degrees)) + (0.084798*math.sin(3*fractional_year_in_degrees)) 


def work(args):

	print "lat:",  convert_deg_min_sec_2_dec(args,45,21,22,'S')
	print "long:", convert_deg_min_sec_2_dec(args,18,5,45,'W')
	print "dec", decimalDegrees2DMS(18.2, "long")
	print "year_frac", calculate_fractional_year_in_degrees(319, 10,35)
	print "sun_dec", calculate_sun_declination(314.849)
	print cal_local_standard_time_meridian(-4)
	print cal_equation_of_time(210)


def render(args, screen):

	# blank the screen
	screen.fill((0,0,0))

	# Draw stuff
	draw_pixels(screen, args.offset)
	args.offset += 1


	# Draw Horizon

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
	args.day_past_percentage = 0.0;
	args.store = my_store(log=log)
	args.key_input_list = []
	args.event = None
	args.lat = 45.4111700
	args.log = -75.6981200

	store_init(args)

	log.set_verbosity(INFO, 0)
	log.set_verbosity(DEBUG, 10)

	run = False




	if pygame.init():
		# Used to manage how fast the screen updates
		clock = pygame.time.Clock()
		pygame.key.set_repeat(1000, 250)
		args.font_handle = pygame.font.Font(None, args.cmd_font)

		screen = pygame.display.set_mode((args.width, args.height), pygame.HWSURFACE | pygame.DOUBLEBUF)
 		time_update(args)
	
 		work(args)

 		args.offset = 0

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
