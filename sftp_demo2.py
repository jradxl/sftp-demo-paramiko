#!/usr/bin/env python3

# Copyright (C) 2003-2007  Robey Pointer <robeypointer@gmail.com>
#
# This file is part of paramiko.
#
# Paramiko is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Paramiko is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Paramiko; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.

# based on code provided by raymond mosteller (thanks!)

# ## John Radley 2018/09/27 ##
# based on Paramiko's demo_sftp.py, but changed to use simpler key authorization
# and tested with proftpd/sftp on Ubuntu 18.04.
# Coded and tested using PyCharm Community, and it's great.

import getpass
import os
import sys
import traceback

import paramiko
from   paramiko.py3compat import input

# setup logging
paramiko.util.log_to_file("sftp_demo2.log")

# Put your defaults here to save typing!!
# If blank, program will request
default_username = ""
default_password = ""
default_hostname = ""
default_passphrase = ""
Port = 2222
UsePasswd=False

# get hostname
username = default_username
if len(sys.argv) > 1:
    hostname = sys.argv[1]
    if hostname.find("@") >= 0:
        username, hostname = hostname.split("@")
else:
    hostname = default_hostname
    if len(hostname) == 0:
        hostname = input("Hostname: ")

if len(hostname) == 0:
    print("*** Hostname required.")
    sys.exit(1)

if hostname.find(":") >= 0:
    hostname, portstr = hostname.split(":")
    Port = int(portstr)

# get username
username = default_username
if default_username == "":
    default_username = getpass.getuser()
    username = input("Username [%s]: " % default_username)
    if len(username) == 0:
        username = default_username

# get password
if UsePasswd:
    if len(default_password) == 0:
        password = getpass.getpass("Password for %s@%s: " % (username, hostname))
    else:
        password = default_password
else:
    password = None

# get passphrase
passphrase = default_passphrase
if not UsePasswd:
    if len(passphrase) == 0:
        passphrase = getpass.getpass("Passphrase: ")

# get host key, if we know one
hostkeytype = None
hostkey = None
try:
    host_keys = paramiko.util.load_host_keys(
        os.path.expanduser("~/.ssh/known_hosts")
    )
except IOError:
    try:
        # try ~/ssh/ too, because windows can't have a folder named ~/.ssh/
        host_keys = paramiko.util.load_host_keys(
            os.path.expanduser("~/ssh/known_hosts")
        )
    except IOError:
        print("*** Unable to open host keys file")
        host_keys = {}

print("Got known_hosts")

if hostname in host_keys:
    hostkeytype = host_keys[hostname].keys()[0]
    hostkey = host_keys[hostname][hostkeytype]
    print("Using host key of type %s" % hostkeytype)

# now, connect and use paramiko Transport to negotiate SSH2 across the connection
try:
    t = paramiko.Transport((hostname, Port))

    rsa_key = None
    if not UsePasswd:
        rsa_key = paramiko.RSAKey.from_private_key_file(os.path.expanduser("~/.ssh/id_rsa"), password=passphrase)
    t.connect(hostkey, username, password, rsa_key)
    sftp = paramiko.SFTPClient.from_transport(t)

    # dirlist on remote host
    dirlist = sftp.listdir(".")
    print("Dirlist: %s" % dirlist)

    # copy this demo onto the server
    try:
        sftp.mkdir("sftp_demo_folder")
    except IOError:
        print("(assuming sftp_demo_folder/ already exists)")
    with sftp.open("sftp_demo_folder/README", "w") as f:
        f.write("This was created by sftp_demo2.py.\n")
    with open("sftp_demo2.py", "r") as f:
        data = f.read()
    sftp.open("sftp_demo_folder/sftp_demo2.py", "w").write(data)
    print("created sftp_demo_folder/ on the server")

    # copy the README back here
    with sftp.open("sftp_demo_folder/README", "r") as f:
        data = f.read()

    ##Needs to be Binary
    with open("README_sftp_demo", "wb") as f:
        f.write(data)
    print("copied README back here")

    # BETTER: use the get() and put() methods
    sftp.put("sftp_demo2.py", "sftp_demo_folder/sftp_demo2a.py")
    sftp.get("sftp_demo_folder/README", "README_demo_sftpa")
    print("Successfully used put and get instead")

    t.close()

except Exception as e:
    print("*** Caught exception: %s: %s" % (e.__class__, e))
    traceback.print_exc()
    try:
        t.close()
    except:
        pass
    sys.exit(1)

## END ##
