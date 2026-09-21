import re

# task 1
log_lines = [
    "2024-01-15 10:02:11 INFO Server started on port 8080",
    "2024-01-15 10:03:47 ERROR Failed to connect to database",
    "2024-01-16 08:15:00 WARNING Disk usage at 85%",
    "2024-01-16 14:22:39 ERROR Timeout while fetching https://example.com/api",
    "2024-01-17 09:00:05 INFO User admin logged in from 192.168.1.10",
    "2024-01-17 11:41:18 DEBUG Cache cleared successfully",
    "2024-01-18 03:12:56 ERROR Connection refused from 192.168.1.55",
    "2024-01-18 23:59:02 INFO Backup completed in 42s",
]

a = [line for line in log_lines if re.match(r"2024-01-16", line)]
print(a)

b = [line for line in log_lines if re.search(r"ERROR|WARNING", line)]
print(b)

c = re.findall(r"\d{1,3}(?:\.\d{1,3}){3}", "\n".join(log_lines))
print(c)

d = [line for line in log_lines if re.search(r"in \d+s$", line)]
print(d)

e = [line for line in log_lines if re.search(r"https?://", line)]
print(e)

f = re.fullmatch(
    r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \w+ .+",
    log_lines[0]
)

print(f is not None)

