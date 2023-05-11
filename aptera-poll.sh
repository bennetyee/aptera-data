#!/bin/bash

poll_period=300
retry_sleep=60

sleep=$poll_period
while sleep ${sleep}
do
	if ! aptera-data > data.new
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
			date -Imin --reference data.new
		       	# so we can run diff -- see show_changed.sh
			mv data.csv data.old
			mv data.new data.csv
			# make a copy available for tom
			scp -p data.csv bennetyee.org:public_html/aptera-data.csv
		else
			echo -n .  # progress
			# rm data.new but leave the turd so we can tell when was the last fetch
		fi
		sleep=$poll_period
	fi
done
