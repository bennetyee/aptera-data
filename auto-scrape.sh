#!/bin/bash

sleep_duration=300

while sleep ${sleep_duration}
do
	if ! ./scrape.py > data.new
	then
		printf 'Connection error?\n'
	fi
	if ! cmp -s data.new data.csv
	then
		date -Imin
#		mail $(whoami) <<EOF
#New investor data has arrived
#EOF
		printf 'New investor data has arrived\a\n'
		mv data.csv data.old  # so i can run diff
		mv data.new data.csv
	else
		echo -n .  # progress
		# rm data.new but leave the turd so we can tell when was the last fetch
	fi
done
