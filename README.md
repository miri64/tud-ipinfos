# Get Infos for IP addresses  

`usage: get-ip-infos.py [-h] [--ip IP] [-f FILE] [-s SEPARATOR] [--col COL] [--out OUT] [--maxmind MAXMIND] [--ipasn IPASN] [--asnames ASNAMES]`

Get infos about single IP address (--ip) or a set of IP addresses in a file by providing the file name (-f) 
File either contains only IP addresses (one per line) or is a dataframe. The ladder needs a
separator (-s -- default is ',') and the column name (--col) of the IP addresses. 
Per default, the data is printed on the screen for a single address or written back into the file with IP addresses (-f) -- you can change that by using the --out option and provide a new filename. 
Default maxmind, ipasn, and asnames path is the same directory of this script, change this using --maxmind, --ipasn, and --asnames
options by providing a path to a directory that contains such files.

```
options:
  -h, --help            show this help message and exit
  --ip IP               Single IP address to get info about
  -f FILE, --file FILE  File name containing IP addresses or a dataframe
  -s SEPARATOR, --separator SEPARATOR
                        Separator used in the dataframe file
  --col COL             Column name containing IP addresses in the dataframe
  --out OUT             Output file name (default: write back to given file name)
  --maxmind MAXMIND     Path to maxmind data directory
  --ipasn IPASN         Path to ipasn data directory
  --asnames ASNAMES     Path to asnames data directory
```

## Example Usage (Single IP)
`./get-ip-infos.py --ip 2001:4860:4860::8888`

Output:

```
Infos for 2001:4860:4860::8888
Geo: US
ASN: 15169
Prefix: 2001:4860::/32
Org: GOOGLE
```

## Example Usage (IP-Address file and database path)
`./get-ip-infos.py --maxmind ../maxmind --asnames ../asnames --ipasn ../ipasn --file testfile01 --out testres01`

Example Output:

```
total          =      50
missing country =       0 (0.0%)
```
Result:

IP infos are written to `testres01`

## Example Usage (Dataframe and database path)
`./get-ip-infos.py --maxmind ../maxmind --asnames ../asnames --ipasn ../ipasn --file testfile01 --out testres01 -s , --col ip-addr`

Example Output:

```
total          =      50
missing country =       0 (0.0%)
```
Result:

IP infos are written to `testres01`

## Requirements
python3
```
maxminddb
geoip2
pyasn
pandas
```
