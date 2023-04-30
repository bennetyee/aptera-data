# Aptera Data

Extract the investor ranking data from Aptera Motor's Accelerator
Program status page.  This code is hacky, but the Accelerator program
will cease in O(months), so there's no need to make it more robust.

The program in `scrape.py` scans the web page at
<https://aptera.us/leaderboard/> for information like the backend XHR
server, and the makes XHR requests to obtain the table data from the
Microsoft Power BI backend.  The table data is written as CSV to
standard output, to be used in the spreadsheet at
<https://tinyurl.com/ApteraAccelerationGraph> to compute statistics
like the expected time until the program ends, etc.  This replaces the
previous method for extracting this data, which was simply a
copy-n-paste from the leaderboard status page to the acceleration
statistics/graphs page.  Selecting all rows from the Power BI page
took many minutes and became untenable as the Accelerator program got
to over ~800 entries.

The program in `auto-scrape.sh` is used in a shell to let me know when
to update the spreadsheet.  It is another quick-and-dirty hack.  The
spreadsheet data upload and cut-n-paste are still manual operations.
