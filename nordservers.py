#!/usr/bin/env python3

import json
import re
import sys
import urllib.request

SERVER_JSON_URL = "https://api.nordvpn.com/v1/servers?limit=9999999"
ALL_SWITCH = '--all'
INCLUDE_OBFUSCATED_SWITCH = '--include-obfuscated'
GET_CONF_SWITCH = '--get-conf'
SHOW_COUNTRIES_SWITCH = '--show-countries'
HOSTNAME_DOMAIN = 'nordvpn.com'
DEFAULT_TRANSPORT = 'tcp'
CATEGORY_MAP = {
    'Dedicated IP': 'dedicated',
    'Double VPN': 'double',
    'Obfuscated Servers': 'obfuscated',
    'Onion Over VPN': 'tor',
    'P2P': 'p2p',
    'Standard VPN servers': 'standard',
}

def stderr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.stderr.flush()

def get_url(url):
    resp = urllib.request.urlopen(url)
    return resp.read().decode()

def main():
    stderr("[*] Fetching %s ... " % SERVER_JSON_URL, end='')
    data = json.loads(get_url(SERVER_JSON_URL))
    stderr("received %s bytes" % len(data))

    countries = list(set([ d['locations'][0]['country']['name'] for d in data ]))
    countries.sort()

    # Show list of countries and exit
    if SHOW_COUNTRIES_SWITCH in sys.argv[1:]:
        for c in countries:
            print(c)
        sys.exit(0)

    # Fetch a config and exit
    if GET_CONF_SWITCH in sys.argv[1:]:
        sys.argv.pop(sys.argv.index(GET_CONF_SWITCH))
        name = sys.argv.pop(1).lower()

        transport = DEFAULT_TRANSPORT
        if len(sys.argv) > 1:
            transport = sys.argv.pop(1)

        if transport not in ['tcp', 'udp']:
            stderr(" ".join([
                "[!] Nord does not know about transport protocol %s." % repr(transport),
                "Please specify 'tcp' or 'udp', or do not specify a transport protocol to use the default (%s)." % repr(DEFAULT_TRANSPORT)
            ]))
            sys.exit(1)

        d = list(filter(lambda x: x['hostname'] == "%s.%s" % (name, HOSTNAME_DOMAIN), data))
        if len(d) == 0:
            stderr(" ".join([
                "[!] Nord does not know about server %s." % repr(name),
                "Use %s to get a list of valid options." % ALL_SWITCH
            ]))
            sys.exit(1)
        d = d[0]

        url_dir = "ovpn_%s" % transport
        if len(list(filter(lambda x: x['identifier'] == 'openvpn_%s' % transport, d['technologies']))) == 0:
            if len(list(filter(lambda x: x['identifier'] == 'openvpn_xor_%s' % transport, d['technologies']))) > 0:
                url_dir = "ovpn_xor_%s" % transport
            else:
                stderr(" ".join([
                    "[!] The Nord server %s does not support the %s transport protocol." % (repr(name), transport),
                    "Use %s to get a list of valid options." % ALL_SWITCH
                ]))
                sys.exit(1)

        url = "https://downloads.nordcdn.com/configs/files/%s/servers/%s.%s.%s.ovpn" % (url_dir, name, HOSTNAME_DOMAIN, transport)
        stderr("[*] Fetching %s ... " % url)
        print(get_url(url))

        if '_xor_' in url_dir:
            stderr('[!] WARNING:  This configuration file is using the "scramble obfuscate" directive, which may require a patched OpenVPN client to work.')

        sys.exit(0)

    # Print a table of all the server records

    # By default this will show one server per config combination with the lowest current load.
    # If ALL_SWITCH is set, it will show all 5000+ servers.
    show_all = False
    if ALL_SWITCH in sys.argv[1:]:
        sys.argv.pop(sys.argv.index(ALL_SWITCH))
        show_all = True

    # By default, obfuscated servers are skipped because they are non-standard.
    include_obfuscated = False
    if INCLUDE_OBFUSCATED_SWITCH in sys.argv[1:]:
        sys.argv.pop(sys.argv.index(INCLUDE_OBFUSCATED_SWITCH))
        include_obfuscated = True

    # Show all servers for the given country, only, if a country is given.
    desired_country = None
    if len(sys.argv) > 1:
        desired_country = ' '.join(sys.argv[1:]).lower()
        if desired_country not in [ c.lower() for c in countries ]:
            stderr(" ".join([
                "[!] Nord does not have an egress in %s." % repr(desired_country.title()),
                "Use %s to get a list of valid options." % SHOW_COUNTRIES_SWITCH
            ]))
            sys.exit(1)

    # This will collect the list of servers to be listed. Collecting all first, rather than
    # printing in each iteration, to calculate the layout of the table.
    servers = []

    for d in data:
        # Map Nord's category names to shorter tags
        _ = list(filter(lambda x: x['title'] in CATEGORY_MAP, d['groups']))
        categories = [CATEGORY_MAP.get(_['title'], _['title']) for _ in _]
        categories.sort()

        # Do not print dedicated servers
        if len(categories) == 0 or 'dedicated' in categories:
            continue

        # Only print obfuscated servers if that flag is present
        if 'obfuscated' in categories and not include_obfuscated:
            continue

        if 'tor' in categories:
            # If it's an onion-backed VPN server we have no way of determining what city or
            # country the client's traffic will come out of.
            country = '???'
            city = '???'
        elif 'double' in categories:
            # If it's a double VPN server we can deduce the country that the client will come out
            # of from it's name, but there is nothing in the API's response to indicate what
            # specific city it will come from.
            m = re.match('.+ - (.+) #\d+', d['name'])
            assert m and m[1] in countries
            country = m[1]
            city = '???'
        else:
            # For non-onion, non-double servers, the egress city and country are the same as
            # the ingress city and country, which is included in the API response.
            country = d['locations'][0]['country']['name']
            city = d['locations'][0]['country']['city']['name']

        # If a particular egress country is desired, only print those servers.
        if desired_country and desired_country != country.lower():
            continue

        servers.append({
            'ID': d['hostname'].replace('.%s' % HOSTNAME_DOMAIN, ''),
            'Name': d['name'],
            'Egress City': city,
            'Egress Country': country,
            'Load': d['load'],
            'Categories': ','.join(categories),
        })

    columns = ['ID', 'Name', 'Egress Country', 'Egress City', 'Categories', 'Load']

    # Determine widths of columns and create format string
    widths = [ len(c) for c in columns ]
    for s in servers:
        for i, c in enumerate(columns):
            widths[i] = max(widths[i], len(str(s[c])))
    fmt = "  ".join(["{:%s.%ss}" % (w, w) for w in widths])

    # Print headings to stderr, so they appear when grepping interactively on the command
    # line and stay out of the way if being piped to another script.
    stderr(fmt.format(*columns))
    stderr(fmt.format(*['-' * 80 for _ in columns]))

    # Print server records
    printed = {}
    for s in sorted(servers, key = lambda i: (i['Egress Country'], i['Egress City'], i['Load'], i['Name'])):
        # If --show-all is not set AND there is no specific desired_country, only show the top
        # hit (i.e., the server with lowest load) for each combination of attributes.
        k = "%s-%s-%s" % (s['Egress Country'], s['Egress City'], s['Categories'])
        if k in printed and not show_all and not desired_country:
            continue
        printed[k] = True

        print(fmt.format(*[str(s[_]) for _ in columns]))


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
