#!/usr/bin/python3
import csv
import sys

def main(argv: list[str]) -> int:
    if len(argv) != 3:
        sys.stderr.write('Usage: compress-coupon-csv in-file out-file\n')
        return 1
    last_value = -1
    with open(argv[1], 'r', newline='') as infile:
        rcsv = csv.reader(infile, delimiter=',', quotechar='"')
        with open(argv[2], 'w', newline='') as outfile:
            wcsv = csv.writer(outfile, delimiter=',', quotechar='"')
            linenum = 0
            for row in rcsv:
                linenum += 1
                print(repr(row))
                if len(row) != 2:
                    sys.stderr.write(f'compress-coupon-csv: Malformed input on line {linenum}: {len(row)} entries\n')
                    return 1
                count = int(row[1])
                if count != last_value:
                    wcsv.writerow(row)
                    last_value = count
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
