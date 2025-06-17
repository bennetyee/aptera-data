# Extracting Publicly Available Data On Aptera Investments

This repository contains various programs used to extract data from
the Aptera website or from Issuance via their API (see
https://kb.issuance.com/issuance-documentation/api/issuer-api for more
info).

## Aptera Accelerator Program Data

Extract the investor ranking data from Aptera Motor's Accelerator
Program status page.  This code is hacky, but the Accelerator program
will cease in O(months), so there's no need to make it more robust.

The program in `aptera-data.py` scans the web page at
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

The program in `aptera-poll.sh` is used in a shell to let me know when
to update the spreadsheet.  It is another quick-and-dirty hack.  The
spreadsheet data upload and cut-n-paste are still manual operations.

## Aptera Priority Delivery and Coupon Investment Round Data

The Aptera Priority Delivery investment offering started in April
2025.  It offers, for investments of $5,000 or more, a "priority
delivery" of an Aptera vehicle, to be delivered after the Accelerator
program vehicles.  There are 1,000 possible priority delivery slots,
first-come-first-serve.

In addition to priority delivery, there is a "coupon" to sweeten the
deal.  For investments $1,000 in the company's stock or more, the
investor receives a coupon for the purchase of the Aptera vehicle
(when/if it becomes available), with the coupon value equal to the
investment amount, up to $10,000.

The number of priority delivery slots are (were) displayed on the top
of every web page on the Aptera web site, in a banner.  The number
displayed is updated using a bit of Javascript code doing queries to
Issuance, where the crowdfunding campaign is run.  Reading that
Javascript code, it's clear that it queries Issuance for a summary
total number of investments and total dollar amount, via the
<tt>/api/investments/summary/</tt> end point -- filtering investments
by requiring them to be on or after the start date of the investment
round, and by requiring the dollar amount of the investments to be
counted to be at or over $5,000 dollars.

The Javascript code uses as filter parameters the at-or-after date as
the start of the priority-delivery / coupon campaign and the $5,000 as
the threshold for counting the number of priority delivery slots
claimed so far.  That is, the filter language is parameterizable --
any date or dollar amount can be used.

Issuance's API includes an API key, but for whatever reason, the use
of the Issuance APIs for the Aptera investment do not require the use
of any API key.  Obviously, if it were required then the publicly
readable Javascript query code would have to have the Firebase ID
Token / API key embedded, which wouldn't really work for access
control.

This is crux of the information leak vulnerability.

Having a way to obtain the total number of investments made at or
after a specified date *and* at or above a specified dollar amount
suffices to extract the date and amount of all the investments made
for this investment round.

The make target <tt>extract_coupon_investments</tt> queries issuance
and outputs all the individual investments made since the start of the
priority delivery / coupon investment round.

The program <tt><a
href="priority_delivery_sanitizer.py">priority_delivery_sanitizer.py</a></tt>
can be used to provide a fake JSON response that returns just the
number of priority-delivery slots claimed.  This program will have to
be modified to make its query with the Firebase ID / API key so it
will have access to the real data, so that it can provide the
controlled interface to just the slot numbers.
