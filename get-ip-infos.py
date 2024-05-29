#!/usr/bin/env python3

import glob
import argparse
import sys
import os

import maxminddb
import geoip2.database
import pyasn

import pandas as pd

from pathlib import Path
from datetime import datetime, timedelta

from functools import lru_cache

class Maxmind:
    def __init__(self, databasefolder):
        dbpath = Path(databasefolder)
        if not dbpath.is_dir():
            print(f"Not a directory: '{databasefolder}'")
            exit()

        self.databasefolder = databasefolder

        self.current_db = None
        self.reader = None

        self.last_checked = datetime.now()

        self.check_interval = timedelta(days=1)

    # -- load database -------------------------------------------------------

    def initialize(self):
        db = self.newest_db()
        if db is None:
            return False
        else:
            self.load_db(db)
            if self.reader is None:
                return False
        return True

    def try_reload(self):
        db = self.newest_db()
        if db is not None and db != self.current_db:
            self.load_db(db)
            self.last_checked = datetime.now()

    def should_check_again(self):
        now = datetime.now()
        if self.last_checked - now >= self.check_interval:
            return True
        else:
            return False

    def newest_db(self):
        pattern = os.path.join(self.databasefolder, "*.mmdb")
        database_list = glob.glob(pattern)
        if len(database_list) == 0:
            return None
        newest_database = max(database_list, key=os.path.getctime)
        self.last_checked = datetime.now()
        return newest_database

    def load_db(self, database):
        # print(f"loading {database}")
        try:
            self.reader = geoip2.database.Reader(database)
            self.current_db = database
        except FileNotFoundError as fnfe:
            print(f"Not a valid file: '{database}' ({fnfe})")
        except PermissionError as pr:
            print(f"Permission error: '{database}' ({pr})")
        except maxminddb.errors.InvalidDatabaseError as ide:
            print(f"Invalid database: '{database}' ({ide})")

    # -- query ---------------------------------------------------------------

    def query(self, ip):
        assert self.reader is not None, "ERR: Load a database before querying."
        try:
            res = self.reader.country(ip)

            name = res.country.name
            iso = res.country.iso_code
            # Not in this database:
            # lat = res.location.latitude
            # lon = res.location.latitude

            return (iso, name)

        except ValueError:
            return (None, None)
        except geoip2.errors.AddressNotFoundError:
            return (None, None)
        except TypeError:
            return (None, None)

class IPasn:
    def __init__(self, databasefolder):
        dbpath = Path(databasefolder)
        if not dbpath.is_dir():
            print(f"Not a directory: '{databasefolder}'")
            exit()

        self.databasefolder = databasefolder

        self.current_db = None
        self.reader = None

        self.last_checked = datetime.now()

        self.check_interval = timedelta(days=1)

    # -- load database -------------------------------------------------------

    def initialize(self):
        db = self.newest_db()
        if db is None:
            return False
        else:
            self.load_db(db)
            if self.reader is None:
                return False
        return True

    def try_reload(self):
        db = self.newest_db()
        if db is not None and db != self.current_db:
            self.load_db(db)
            self.last_checked = datetime.now()

    def should_check_again(self):
        now = datetime.now()
        if self.last_checked - now >= self.check_interval:
            return True
        else:
            return False

    def newest_db(self):
        pattern = os.path.join(self.databasefolder, "ipasn_*.gz")
        database_list = glob.glob(pattern)
        if len(database_list) == 0:
            return None
        newest_database = max(database_list, key=os.path.getctime)
        self.last_checked = datetime.now()
        return newest_database

    def load_db(self, database):
        try:
            reader = pyasn.pyasn(database)
            self.reader = reader
            self.current_db = database

        except FileNotFoundError as fnfe:
            print(f"Not a valid file: '{database}' ({fnfe})")
        except PermissionError as pr:
            print(f"Permission error: '{database}' ({pr})")

    # -- query ---------------------------------------------------------------

    def query(self, ip):
        assert self.reader is not None, "ERR: Load a database before querying."
        try:
            asn, prefix = self.reader.lookup(ip)

            if asn is not None:
                asn = int(asn)

            return (asn, prefix)

        except ValueError as ve:
            print(f"No data for address: '{ip}' ({ve})")
            return (None, None)
        except TypeError as te:
            print(f"Not a valid type: '{ip}' ({te})")
            return (None, None)

class ASname:
    def __init__(self, databasefolder):
        dbpath = Path(databasefolder)
        if not dbpath.is_dir():
            print(f"Not a directory: '{databasefolder}'")
            exit()

        self.databasefolder = databasefolder

        self.current_db = None
        self.reader = None

        self.last_checked = datetime.now()

        self.check_interval = timedelta(days=1)

    # -- load database -------------------------------------------------------

    def initialize(self):
        db = self.newest_db()
        if db is None:
            return False
        else:
            self.load_db(db)
            if self.reader is None:
                return False
        return True

    def try_reload(self):
        db = self.newest_db()
        if db is not None and db != self.current_db:
            self.load_db(db)
            self.last_checked = datetime.now()

    def should_check_again(self):
        now = datetime.now()
        if self.last_checked - now >= self.check_interval:
            return True
        else:
            return False

    def newest_db(self):
        pattern = os.path.join(self.databasefolder, "asnames-*.csv.gz")
        database_list = glob.glob(pattern)
        if len(database_list) == 0:
            return None
        newest_database = max(database_list, key=os.path.getctime)
        self.last_checked = datetime.now()
        return newest_database

    def load_db(self, database):
        try:
            self.reader = (
                pd.read_csv(
                    database,
                    sep="|",
                    header=None,
                    index_col=[0],
                    usecols=[0, 1],
                )
                .squeeze("columns")
                .to_dict()
            )
            self.current_db = database
        except FileNotFoundError as fnfe:
            print(f"Not a valid file: '{database}' ({fnfe})")
        except PermissionError as pr:
            print(f"Permission error: '{database}' ({pr})")

    # -- query ---------------------------------------------------------------

    def query(self, ip):
        assert self.reader is not None, "ERR: Load a database before querying."
        try:
            if ip in self.reader:
                return self.reader[ip]
            else:
                return None

        except ValueError as ve:
            print(f"No data for address: '{ip}' ({ve})")
            return None
        except TypeError as te:
            print(f"Not a valid type: '{ip}' ({te})")
            return (None, None)

@lru_cache(maxsize=10000)
def lookup_asn(asndb, addr):
    # asn, prefix = ipasn.query(saddr)
    asn, _ = asndb.query(addr)
    return asn

@lru_cache(maxsize=10000)
def lookup_prefix(asndb, addr):
    # asn, prefix = ipasn.query(saddr)
    _, prefix = asndb.query(addr)
    return prefix

@lru_cache(maxsize=10000)
def lookup_geo(geodb, addr):
    # iso, _ = mm.query(saddr)
    iso, _ = geodb.query(addr)
    return iso

@lru_cache(maxsize=10000)
def lookup_org(orgdb, asn):
    # org = asname.query(asn)
    return orgdb.query(asn)


def get_infos(maxmindpath, ipasnpath, asnamepath, df,addrcolumn,singleip=False):

    # -- check paths ---------------------------------------------------------

    if not Path(maxmindpath).is_dir():
        print("ERR: maxmind path is not a directory!")
        return
    
    if not Path(ipasnpath).is_dir():
        print("ERR: please select a directory with --ipasn-db")
        return

    if not Path(asnamepath).is_dir():
        print("ERR: please select a directory with --asname-db")
        return
    

# # -- initialize meta data stuff ------------------------------------------

    # Initialize Maxmind database
    mm = Maxmind(maxmindpath)
    if not mm.initialize():
        print(f"ERR: could not load Maxmind database from {maxmindpath}")
        return
    
    # Initialize pyasn database.
    ipasn = IPasn(ipasnpath)
    if not ipasn.initialize():
        print(f"ERR: could not load ipasn database from {ipasnpath}")
        return

    # Initialize AS name database.
    asname = ASname(asnamepath)
    if not asname.initialize():
        print(f"ERR: could not load as-to-name database from {asnamepath}")
        return

    if singleip:
        asn = lookup_asn(ipasn,df)
        print(f'Infos for {df}\nGeo: {lookup_geo(mm,df)}\nASN: {asn}\nPrefix: {lookup_prefix(ipasn,df)}\nOrg: {lookup_org(asname,asn)}')
    else:
        df['Geo'] = df[addrcolumn].apply(lambda ip: lookup_geo(mm, ip))
        df['AS-Number'] = df[addrcolumn].apply(lambda ip: lookup_asn(ipasn, ip))
        df['BGP-Prefix'] = df[addrcolumn].apply(lambda ip: lookup_prefix(ipasn, ip))
        df['Org'] = df['AS-Number'].apply(lambda asn: lookup_org(asname, asn))
        total = len(df.index)
        pre_missing = df['BGP-Prefix'].isnull().sum()
        cou_missing = df['Geo'].isnull().sum()
        asn_missing = df['AS-Number'].isnull().sum()
        org_missing = df['Org'].isnull().sum()
        print(f"total          = {total:>7}")
        print(
            f"missing country = {cou_missing:>7} ({round(cou_missing / total * 100, 2)}%)"
        )

# Default paths for maxmind, ipasn, asnames
maxmindpath = './maxmind/'
ipasnpath = './ipasn/'
asnamepath = './asnames/'

# Default field with IP address
field = 'ip-addr'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=(
        "Get infos about single IP address (--ip) or a set of IP addresses in a file by providing the file name (-f)\n"
        "File either contains only IP addresses (one per line) or is a dataframe, then a separator (-s) and the column name (--col) are mandatory.\n"
        "Per default, the data is printed on the screen for a single address, or written into the provided filename -- you can change that by using the --out option and provide a new filename.\n"
        "Default maxmind, ipasn, and asnames path is the same directory of this script, change this using --maxmind, --ipasn, and --asnames options."
    ))

    parser.add_argument('--ip', type=str, help='Single IP address to get info about')

    # File with IP addresses
    parser.add_argument('-f', '--file', type=str, help='File name containing IP addresses or a dataframe')

    # Separator for dataframe
    parser.add_argument('-s', '--separator', type=str, help='Separator used in the dataframe file', default=',')

    # Column name for IP addresses in dataframe
    parser.add_argument('--col', type=str, help='Column name containing IP addresses in the dataframe')

    # Output file
    parser.add_argument('--out', type=str, help='Output file name (default: write back to given file name)')

    # Maxmind, ipasn, and asnames paths
    parser.add_argument('--maxmind', type=str,help='Path to maxmind data directory')
    parser.add_argument('--ipasn', type=str,help='Path to ipasn data directory')
    parser.add_argument('--asnames', type=str,help='Path to asnames data directory')

    args = parser.parse_args()

    if args.maxmind:
        maxmindpath = args.maxmind
    if args.ipasn:
        ipasnpath = args.ipasn
    if args.asnames:
        asnamepath = args.asnames
    if args.ip:
        get_infos(maxmindpath, ipasnpath, asnamepath, args.ip,field,singleip=True)
    elif args.file:
        if not args.col:
            df = pd.read_csv(args.file,sep=args.separator,names=[field])
        else:
            field=args.col
            df = pd.read_csv(args.file,sep=args.separator)
        get_infos(maxmindpath, ipasnpath, asnamepath, df,field)
        if args.out:
            df.to_csv(args.out,sep=args.separator,index=False)
        else:
            df.to_csv(args.file,sep=args.separator,index=False)
    else:
        print('[*] You need to specify a single IP address (--ip) or provide a filename with IP addresses to check (-f or --file).')
        exit(-1)



