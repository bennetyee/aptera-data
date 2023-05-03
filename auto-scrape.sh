#!/bin/bash

poll_period=300
retry_sleep=60

sleep=$poll_period
while sleep ${sleep}
do
	if ! ./scrape.py > data.new
	then
		printf 'Connection error?\n'
		sleep=$retry_sleep
	else
		if ! cmp -s data.new data.csv
		then
#			mail $(whoami) <<EOF
#New investor data has arrived
#EOF
			printf '\nNew investor data has arrived\a\n'
			date -Imin
			mv data.csv data.old  # so i can run diff
			mv data.new data.csv
		else
			echo -n .  # progress
			# rm data.new but leave the turd so we can tell when was the last fetch
		fi
		sleep=$poll_period
	fi
done
