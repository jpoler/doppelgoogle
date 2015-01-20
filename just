LOGDIR=/tmp/crawl

default: crawl

start:
	@bash --init-file env/bin/activate -i

neoup:
	@echo 'Starting neo...'
	@~/neo4j/bin/neo4j start
	@echo 'Neo started!'

crawl:
	@python dg.py --crawl http://www.google.com

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

	
	