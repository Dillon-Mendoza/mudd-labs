import os
import re

# Items to find: Hostname, sshd id, timestamp, auth method, username, UID, Outcome
# Will be using multiple examples of sshd logs to create the needed regex expressions to parse data correctly in real-time


# Line is a general log
line = "Apr 26 21:48:19 localhost.localdomain sshd-session[179448]: pam_unix(sshd:session): session opened for user mudd-fedora(uid=1000) by mudd-fedora(uid=0)"

# Line2 is a failed log entry
line2 = "Apr 26 18:41:15 localhost.localdomain sshd-session[178200]: Failed password for invalid user mudd from 100.93.55.19 port 42124 ssh2"

# Line3 is an accepted log entry
line3 = "Apr 26 18:42:00 localhost.localdomain sshd-session[178204]: Accepted password for mudd-fedora from 100.93.55.19 port 46160 ssh2"

# Line4 is an invalid log entry
line4 = "Apr 26 18:41:08 localhost.localdomain sshd-session[178200]: Invalid user mudd from 100.93.55.19 port 42124"


# IP address portion of script
addr = re.search(r"\d+\.\d+\.\d+\.\d+", line4)

# sshd id number portion of script
sshd_id = re.search(r"\[\d+\]", line)
clean_sshd_id = sshd_id.group().strip("[]")


# Hostname portion of script
hostname = re.search(r"[a-zA-Z0-9]+\.[a-zA-z0-9]\S+", line)
clean_hostname = hostname.group()


# Timestamp portion of script
timestamp = re.search(r"[a-zA-z]\w+\s[0-9]\w+\s\d+\d+\:\d+\d+\:\d+\d+", line)
clean_timestamp = timestamp.group()


# Username portion of script
username = re.search(r"\buser\s([a-zA-z0-9]\S[^()]+)", line)
clean_username = username.group(1)


# UID portion of script
UID = re.search(r"\buid=(\d+)", line)
clean_uid = UID.group(1)


# Auth method and outcome (accepted, invalid or failed) portion of script.
# Variable name will be amo (auth method/outcome)
amo = re.search(r"\b(Accepted|Failed|Invalid)\s(\S+)", line2)
print(amo.group(1))
print(amo.group(2))


# Test output of all of the data parsed from regex expressions
#print(f"Current parsed ssh data shows log number {clean_sshd_id} for {clean_hostname} at {clean_timestamp} from \n{clean_username}, UID={clean_uid}, soon to be more!")