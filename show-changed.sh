#!/bin/bash

diff <(cut -d, -f2- data.old) <(cut -d, -f2- data.csv)
