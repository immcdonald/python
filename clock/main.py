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

	sunset = time_to_seconds(18,6,00)
	sunset_percent =  seconds_to_percent_of_day(sunset)
	args.log.out(str(sunset_percent)+" --> "+str(args.day_past_percentage))
	pygame.time.set_timer(DEF_TIME_UPDATE_EVENT, 500);


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
	args.day_past_percentage = 0.0;
	args.store = my_store(log=log)

	store_init(args)

	log.set_verbosity(INFO, 0)
	log.set_verbosity(DEBUG, 10)

	run = True

	if pygame.init():
		screen = pygame.display.set_mode((args.width, args.height), pygame.HWSURFACE | pygame.DOUBLEBUF)
 		time_update(args)

		while(run):
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					run = False
				elif event.type == DEF_TIME_UPDATE_EVENT:
 					time_update(args)

 	log.out("Good Bye")

if __name__ == "__main__":
	main(sys.argv[1:])
