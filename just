default: crawl

start:
	@bash --init-file env/bin/activate -i

neoup:
	@echo 'Starting neo...'
	@~/neo4j/bin/neo4j start
	@echo 'Neo started!'

crawl:
	python crawl.py

edit:
	vi crawl.py
