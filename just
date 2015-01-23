LOGDIR=/tmp/crawl

default: crawl

test:
	python /home/jdp/doppelgoogle/doppelgoogle/db/test_inserts.py

neoup:
	@echo 'Starting neo...'
	@~/neo4j/bin/neo4j start
	@echo 'Neo started!'

crawl:
	@python dg.py --crawl en.wikipedia.org/Computer

z:
	@echo 'Zombie processes:'
	@echo `ps -A | grep python`

log:
	@cat $(LOGDIR)/* | sort

setup:
	@echo 'Initializing a virtual environment'
	@virtualenv env
	@echo 'Activating virtualenv and installing python dependencies'
	@cat setup | bash --init-file env/bin/activate -i -s -x
	@bash --init-file env/bin/activate -i

	
	