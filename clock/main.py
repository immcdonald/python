import os, sys
import argparse
import pygame
from pygame.locals import *

parentPath = os.path.abspath("../common")

if parentPath not in sys.path:
	sys.path.insert(0, parentPath)

from my_log import *


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
	log.set_verbosity(INFO, 0)
	log.set_verbosity(DEBUG, 10)

	run = True

	if pygame.init():
		screen = pygame.display.set_mode((args.width, args.height), pygame.HWSURFACE | pygame.DOUBLEBUF)

		while(run):
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					run = False

if __name__ == "__main__":
	main(sys.argv[1:])
