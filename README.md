# nordservers.py

A handy little script to get information about and OpenVPN configuration for NordVPN's various servers.

## Usage

Run without any arguments to get the top (lowest load) server ID, name, country egress, city egress, categories (features), and current load for each combination of egress location and categories:

```
% ./nordservers.py | head
[*] Fetching https://api.nordvpn.com/v1/servers?limit=9999999 ... received 5322 bytes
ID         Name                              Egress Country          Egress City     Categories    Load
---------  --------------------------------  ----------------------  --------------  ------------  ----
ch-onion2  Switzerland Onion #2              ???                     ???             tor           15
al24       Albania #24                       Albania                 Tirana          p2p,standard  16
al18       Albania #18                       Albania                 Tirana          standard      25
ar46       Argentina #46                     Argentina               Buenos Aires    standard      54
au527      Australia #527                    Australia               Adelaide        p2p,standard  2
au642      Australia #642                    Australia               Brisbane        p2p,standard  11
au598      Australia #598                    Australia               Melbourne       p2p,standard  5
au573      Australia #573                    Australia               Perth           p2p,standard  5
au656      Australia #656                    Australia               Sydney          p2p,standard  3
at123      Austria #123                      Austria                 Vienna          p2p,standard  4
```

Run with the `--all` switch to get a list of ALL current NordVPN servers, ordered by egress location and then current load:

```
% ./nordservers.py --all | head
[*] Fetching https://api.nordvpn.com/v1/servers?limit=9999999 ... received 5321 bytes
ID         Name                              Egress Country          Egress City     Categories    Load
---------  --------------------------------  ----------------------  --------------  ------------  ----
ch-onion2  Switzerland Onion #2              ???                     ???             tor           17
nl-onion4  Netherlands Onion #4              ???                     ???             tor           46
al24       Albania #24                       Albania                 Tirana          p2p,standard  9
al19       Albania #19                       Albania                 Tirana          p2p,standard  16
al18       Albania #18                       Albania                 Tirana          standard      26
al26       Albania #26                       Albania                 Tirana          standard      36
al21       Albania #21                       Albania                 Tirana          standard      47
al20       Albania #20                       Albania                 Tirana          standard      49
al23       Albania #23                       Albania                 Tirana          standard      52
ar46       Argentina #46                     Argentina               Buenos Aires    standard      52
```

"Obfuscated" servers are excluded, by default.  If you want to include them, toss the `--include-obfuscated` switch on:

```
% ./nordservers.py --include-obfuscated | grep obfuscated | head
[*] Fetching https://api.nordvpn.com/v1/servers?limit=9999999 ... received 5320 bytes
ID         Name                              Egress Country          Egress City     Categories    Load
---------  --------------------------------  ----------------------  --------------  ------------  ----
ca1531     Canada #1531                      Canada                  Toronto         obfuscated    7
fr782      France #782                       France                  Paris           obfuscated    11
de1010     Germany #1010                     Germany                 Berlin          obfuscated    12
de1013     Germany #1013                     Germany                 Frankfurt       obfuscated    3
hk259      Hong Kong #259                    Hong Kong               Hong Kong       obfuscated    1
it208      Italy #208                        Italy                   Milan           obfuscated    3
jp597      Japan #597                        Japan                   Tokyo           obfuscated    1
nl948      Netherlands #948                  Netherlands             Amsterdam       obfuscated    9
sg311      Singapore #311                    Singapore               Singapore       obfuscated    0
se540      Sweden #540                       Sweden                  Stockholm       obfuscated    7
```

Run with the `--show-countries` switch to get a list of all the counties where NordVPN currently has any egress:

```
% ./nordservers.py --show-countries | head
[*] Fetching https://api.nordvpn.com/v1/servers?limit=9999999 ... received 5321 bytes
Albania
Argentina
Australia
Austria
Belgium
Bosnia and Herzegovina
Brazil
Bulgaria
Canada
Chile
```

Pass along one of those countries to get a list of all NordVPN's servers that egress, there:

```
% ./nordservers.py south africa | head
[*] Fetching https://api.nordvpn.com/v1/servers?limit=9999999 ... received 5324 bytes
ID     Name               Egress Country  Egress City   Categories    Load
-----  -----------------  --------------  ------------  ------------  ----
za109  South Africa #109  South Africa    Johannesburg  p2p,standard  15
za79   South Africa #79   South Africa    Johannesburg  p2p,standard  15
za111  South Africa #111  South Africa    Johannesburg  p2p,standard  19
za61   South Africa #61   South Africa    Johannesburg  p2p,standard  19
za78   South Africa #78   South Africa    Johannesburg  p2p,standard  19
za110  South Africa #110  South Africa    Johannesburg  p2p,standard  21
za124  South Africa #124  South Africa    Johannesburg  p2p,standard  22
za118  South Africa #118  South Africa    Johannesburg  p2p,standard  23
za76   South Africa #76   South Africa    Johannesburg  p2p,standard  24
za80   South Africa #80   South Africa    Johannesburg  p2p,standard  25
```

When you've selected a server and want to retrieve the OpenVPN configuration file for it, use the `--get-conf` switch along with the ID of that server:

```
% ./nordservers.py --get-conf nl-se8 | head
[*] Fetching https://api.nordvpn.com/v1/servers?limit=9999999 ... received 5319 bytes
[*] Fetching https://downloads.nordcdn.com/configs/files/ovpn_tcp/servers/nl-se8.nordvpn.com.tcp.ovpn ...
client
dev tun
proto tcp
remote 213.232.87.174 443
resolv-retry infinite
remote-random
nobind
tun-mtu 1500
tun-mtu-extra 32
mssfix 1450
```

...by default, that will get the TCP flavor of the .conf.  If you would prefer UDP, simply indicate `udp` after the server ID:

```
% ./nordservers.py --get-conf nl-se8 udp | head
[*] Fetching https://api.nordvpn.com/v1/servers?limit=9999999 ... received 5319 bytes
[*] Fetching https://downloads.nordcdn.com/configs/files/ovpn_udp/servers/nl-se8.nordvpn.com.udp.ovpn ...
client
dev tun
proto udp
remote 213.232.87.174 1194
resolv-retry infinite
remote-random
nobind
tun-mtu 1500
tun-mtu-extra 32
mssfix 1450
```



## License
[MIT](https://en.wikipedia.org/wiki/MIT_License)

## Author Information
This script was created and is maintained by [CofenseLabs](https://cofenselabs.com/).
