LOGDIR=/tmp/crawl

default: crawl

start:
	@bash --init-file env/bin/activate -i

neoup:
	@echo 'Starting neo...'
	@~/neo4j/bin/neo4j start
	@echo 'Neo started!'

crawl:
	python crawl.py

z:
	@echo 'Zombie processes:'
	@echo `ps -A | grep python`

log:
	cat $(LOGDIR)/* | sort

tlog:
	python logger.py

setup:
	@echo 'Initializing a virtual environment'
	@virtualenv env
	@echo 'Activating virtualenv'
	@bash --init-file env/bin/activate -i
	@echo 'installing dependancies'
	@pip install -r requirements.txt
	@echo 'Adding doppelgoogle to PYTHONPATH'
	@projdir=${PWD##*/}
	@cd .. && echo `pwd` > $projdir/env/lib/python2.7/site-packages/doppelgoogle.pth
	@cd $projdir
	@echo 'All done!'
	
	