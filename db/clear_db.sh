#!/bin/bash

DB_PATH=/home/jdp/neo4j/data
NEO4J=/home/jdp/neo4j/bin/neo4j

$NEO4J stop
rm -rf $DB_PATH && mkdir -p $DB_PATH
$NEO4J start

