#!/bin/bash

poll_period=300
retry_sleep=60
update_remote=1
keep_hist=1
history_dir=${1:-history}

sleep=1  # fast check on first time through
while sleep ${sleep}
do
	if ! aptera_data > data.new
	then
		printf 'Connection error occured at %s.\n' "$(date -Imin)"
		sleep=$retry_sleep
	else
		now="$(date -Imin --reference data.new)"
		if ! cmp -s data.new data.csv
		then
#			mail $(whoami) <<EOF
#New investor data has arrived
#EOF
			printf '\nNew investor data has arrived\a\n%s\n' "$now"
			if [ $keep_hist -eq 1 ]
			then
				mkdir -p $history_dir
				cp -p data.new $history_dir/data.$now.csv
			fi
		       	# so we can run diff -- see show_changed.sh
			mv data.csv data.old
			mv data.new data.csv
			# make a copy available for tom
			[ $update_remote -eq 1 ] && scp -p data.csv bennetyee.org:public_html/aptera-data.csv
		else
			echo -n .  # progress
			# rm data.new but leave the turd so we can tell when was the last fetch
		fi
		sleep=$poll_period
	fi
done
