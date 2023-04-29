#!/usr/bin/python3

import os
import re
import sys
import time
import argparse
import base64
import bs4
import json
import requests
import urllib

options = None  # argparse.Namespace

main_url='https://aptera.us/leaderboard/'

url='https://app.powerbi.com/view?r=eyJrIjoiZGZhODZhYmUtZjQ3My00NjViLWI3OWEtYWFkNzJjYWU0MzdiIiwidCI6ImU0ZGU0MGIzLTU3ODYtNDAyMC05YjcxLWNmOTM3NjE5ZTRkNiIsImMiOjZ9'

def fetch_data(url):
    r = requests.get(url)
    return bs4.BeautifulSoup(r.text, 'lxml')

def find_js_var_init(varname, text):
    regex = varname + r' *= *\'(.*?)\''
    m = re.search(regex, text)
    if m is None:
        sys.stderr.write(f'Not found: {varname}\n')
        return None
    return m.group(1)

def xhr_request_headers(activity_id, request_id, resource_key):
    return {
        'Accept': 'application/json',
        'ActivityId': activity_id,
        'RequestId': request_id,
        'X-PowerBI-ResourceKey': resource_key,
    }

def find_all_vars(vlist, data):
    return dict([(v, find_js_var_init(v, data)) for v in vlist])

def remove_suffix(s, suffix):
    if s.endswith(suffix):
        s = s[:-len(suffix)]
    return s

def remove_prefix(s, prefix):
    if s.startswith(prefix):
        s = s[len(prefix):]
    return s

def get_APIM_url(cluster_uri):
    parsed = urllib.parse.urlparse(cluster_uri)
    t = parsed.netloc.split('.')
    t[0] = remove_suffix(t[0], '-redirect')
    t[0] = remove_prefix(t[0], 'global-')
    t[0] = t[0] + '-api'
    return f'{parsed.scheme}://{".".join(t)}'

def fetch_data():
    global url

    if options.check_main_page:
        main_page = requests.get(main_url)
        m = re.search(r'<iframe.*nitro-lazy-src="(.*powerbi.*?)".*</iframe>', main_page.text)
        if m is None:
            sys.stderr.write('iframe source not found\n')
            return 1
        if options.verbose > 0:
            print(len(m.group(1)))
        if m.group(1) != url:
            sys.stderr.write('Warning: powerbi address changed\n')
            sys.stderr.write(f' was {url}\n')
            sys.stderr.write(f' now {m.group(1)}\n')
            url = m.group(1)

    m = re.search(r'\?r=(.*)', url)
    if m is None:
        sys.stderr.write('iframe r parameter unparseable')
        return 2

    query_string = m.group(1)
    query_string = urllib.parse.unquote(query_string)
    query_json_str = base64.b64decode(query_string)
    query_json = json.loads(query_json_str)
    tenant_id = query_json['t']
    resource_key = query_json['k']

    if options.verbose > 0:
        print(f'tenant_id = \'{tenant_id}\', resource_key = \'{resource_key}\'')

    if options.use_canned_iframe_data is not None:
        with open(options.use_canned_iframe_data) as f:
            frame_data = f.read()
    else:
        request_result = requests.get(url)
        frame_data = request_result.text


    vlist = [
        'telemetrySessionId',
        'wfeClusterName',
        'appInsightsV2InstrKey',
        'cdnUrl',
        'clusterUri',

        'getExplorationUrl',
        'getConceptualSchemaUrl',
        'queryDataUrl',
        'resourceLoaderUrl',
        'routingUrl',

        'resolvedClusterUri',
    ]
    vmap = find_all_vars(vlist, frame_data)
    if options.verbose > 1:
        print(f'vmap = {vmap}')

    req_map = {}
    # get function names and requestId
    fn_name = ''
    fn_re = re.compile(r'function +([a-zA-Z0-9]+)\(')
    request_re = re.compile(r'requestId *= *\'([-0-9a-zA-Z]+)\'')
    for line in frame_data.split('\n'):
        if line.endswith(r'\'):
            line = line[:-1]
        m = fn_re.search(line)
        if m is not None:
            fn_name = m.group(1)
        m = request_re.search(line)
        if m is not None:
            req_map[fn_name] = m.group(1)

    if options.verbose > 1:
        print(f'req_map = {req_map}')

    headers = xhr_request_headers(vmap['telemetrySessionId'],
                                  req_map['resolveCluster'],
                                  resource_key)

    headers['referer'] = url
    # u = f'{get_APIM_url(vmap["resolvedClusterUri"])}{vmap["routingUrl"]}{tenant_id}'
    # print(f'URL={u}')
    # conn = requests.get(u, headers=headers)
    # print(f'conn.content = {conn.content}')
    # print(f'conn.headers = {conn.headers}')
    # print(f'conn.status_code = {conn.status_code}')

    u = f'{get_APIM_url(vmap["resolvedClusterUri"])}{vmap["queryDataUrl"]}?synchronous=true'
    if options.verbose > 2:
        print(f'URL={u}')
    with open(options.request_file, 'rb') as f:
        req = f.read()
    # DatasetId, ReportId, VisualId are GUIDs in the request.  We are just
    # using canned ones, and if they change we won't know.  These IDs are
    # presumably obtained via execution some other XHR requests, which we
    # are eliding.
    #
    # The request is obtained by using Chrome developer mode and
    # copying an actual request that was transmitted.  The "CacheKey"
    # entries is deleted.
    conn = requests.post(u, req, headers=headers)
    if options.reply_log_file is not None:
        with open(options.reply_log_file, 'wb') as f:
            f.write(conn.content)
    return json.loads(conn.content)


def process():
    if options.load_xhr_response is not None:
        if options.verbose > 0:
            print(f'Loading canned data from file "{options.load_xhr_response}"')
        with open(options.load_xhr_response, 'rb') as f:
            resp = json.loads(f.read())
    else:
        resp = fetch_data()

    # This is a complicated JSON object.  Sigh.
    results = resp['results']
    # results is a list of dicts containing 'jobId' and 'result' as keys
    # there was only one job, so len(results) should be 1.
    assert len(results) == 1
    query_result = results[0]['result']
    data = query_result['data']
    dsr = data['dsr']
    ds = dsr['DS']
    ds0 = ds[0]
    row_data = ds0['PH']  # encoded
    # row_data[0]['DM0'] is list of row data
    #  "C" key to list:
    #    rank, country, timestamp?, initials, state, investmentid, $-since-jan-27, $-total.
    #    rank, timestamp, country, initials, state, investmentId, $-since-jan27,$-total
    #  "C"s with "R"
    #    rank, timestamp, initials, state, investmentId, $-since, $-total, R=?
    #    rank, timestamp, initials, state, investmentId, $-total
    value_dicts = ds0['ValueDicts']
    # D0 country codes, D1 initials, D2 states, D3 Investment Id
    country_codes = value_dicts['D0']
    initials = value_dicts['D1']
    states = value_dicts['D2']
    investment_ids = value_dicts['D3']

    parsed = []
    print(f'There are {len(row_data[0]["DM0"])} rows')
    rnum = 0
    v = {}
    for row in row_data[0]['DM0']:
        if options.verbose > 1:
            print(f'{rnum}: {row}')
        rnum = rnum + 1
        record = row['C']
        r = row.get('R', 0)
        o_slash = row.get('Ø', 0)
        country = 0  # US default?

        uncertain=''  # when decode is uncertain, change to visible marker

        # r appears to be binary encoded for which is NOT updated
        # from the previous entry, so r=0 means everything is present
        # and r&1 means rank is the same (which will never occur), and
        # r&2 means country is the same
        #
        # o_slash are entries that are blanked, rather than inherited

        fields = ['rank', 'country', 'timestamp', 'inits', 'st', 'inv', 'accel', 'alltime']

        rcopy = record[:]
        for ix in range(len(fields)):
            omit = (o_slash & 1) != 0
            o_slash = o_slash // 2
            take = (r & 1) == 0
            r = r // 2
            if not take:
                continue
            if omit:
                v[fields[ix]] = '  '
            else:
                v[fields[ix]] = record[0]
                record = record[1:]
        if options.verbose > 1:
            print(f'{v}')
        if isinstance(v['inv'], str):
            inv_str = v['inv']
        else:
            inv_str = investment_ids[v['inv']]
        if isinstance(v['st'], str):
            st_str = v['st']
        else:
            st_str = states[v['st']]
        if isinstance(v['inits'], str):
            init_str = v['inits']
        else:
            init_str = initials[v['inits']]
        if isinstance(v['country'], str):
            country_str = v['country']
        else:
            country_str = country_codes[v['country']]
        print(f'{v["rank"]}, {init_str}, {st_str}, {country_str}, {inv_str}, {format_time(v["timestamp"])}, ${v["accel"]:,.1f}, ${v["alltime"]:,.2f}{uncertain}')

        
def format_time(msecs):
    gm = time.gmtime(msecs/1000)
    return time.strftime('%m/%d/%Y %I:%M %p', gm)

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-main-page', '-c', type=bool, default=False,
                        action=argparse.BooleanOptionalAction,
                        help='check main page for PowerBI iframe URL')
    parser.add_argument('--use-canned-iframe-data', '-C', type=str,
                        default=None,
                        help='filename where canned iframe data is loaded from')
    parser.add_argument('--request-file', '-r', type=str, default='request.txt',
                        help='file containing XHR data query')
    parser.add_argument('--reply-log-file', '-w', type=str, default=None,
                        help='file into which the XHR data query reply should be written')
    parser.add_argument('--load-xhr-response', '-x', type=str, default=None,
                        help='load test XHR response from file instead of loading from web endpoints')
    parser.add_argument('--verbose', '-v', action='count',
                        default=0,
                        help='increment the verbosity level by 1')
    global options
    options = parser.parse_args(sys.argv[1:])
    process()
    return 0

if __name__ == '__main__':
    # os.environ['all_proxy'] = 'socks5://localhost:1234'
    # os.environ['ALL_PROXY'] = 'socks5://localhost:1234'
    sys.exit(main(sys.argv))
