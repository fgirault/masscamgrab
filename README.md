masscamgrab
===========

A command line tool to grab pictures from a large set of webcams, implemented 
in pure python.

	Usage: masscamgrab.py [options]

	Options:
	  -h, --help            show this help message and exit
	  -i INPUT, --input=INPUT
	                        path to a file containing one url per line
	  -o OUTPUT, --output=OUTPUT
	                        output directory
	  -p PARALLEL, --parallel=PARALLEL
	                        number of subprocesses.Don't hesitate to try high
	                        values like 64 or 128 ;)

The input file must contain one url per line. If getting content from an url 
fails, the url is added to a fail.log file in the current directory.

A common form of url is http://[ip adress]:80/anony/mjpg.cgi

Timestamped pictures are created in a directory per host in the output directory.
