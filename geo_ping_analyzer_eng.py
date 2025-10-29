import subprocess
import time
import sys
from datetime import datetime
import statistics

# --- CONFIGURATION ---
# List of global targets with known approximate geographic coordinates
# Reliable public DNS servers are used for the widest possible geographic coverage (worldwide).
TARGETS = {
# North America
"Google_US_E": {"ip": "8.8.8.8", "location": "Virginia/California, United States (North America)"},
"OpenDNS_US_W": {"ip": "208.67.222.222", "location": "San Francisco, United States (West)"},

# South America
"Google_BR": {"ip": "8.8.4.4", "location": "Sao Paulo, Brazil (South America)"},

# Europe
"Cloudflare_EU": {"ip": "1.1.1.1", "location": "Frankfurt/London, Germany/United Kingdom (Europe)"},
"Quad9_EU": {"ip": "9.9.9.9", "location": "Zurich/Amsterdam" (Europe)"},
"Yandex_RU": {"ip": "77.88.8.8", "location": "Moscow, Russia (Eurasia)"},

# Africa
"OpenDNS_ZA": {"ip": "196.43.46.190", "location": "Johannesburg, South Africa (Africa)"},

# Asia (East and Southeast)
"AliDNS_CN": {"ip": "223.5.5.5", "location": "Beijing/Shanghai, China (East Asia)"},
"Hinet_TW": {"ip": "168.95.1.1", "location": "Taipei, Taiwan (East Asia)"},

# Oceania/Australia
"Cloudflare_AU": {"ip": "1.0.0.1", "location": "Sydney, Australia (Oceania)"},
}

# Number of packets to send to each target
PING_COUNT = 3
# Timeout for each individual packet (in seconds)
PING_TIMEOUT_PER_PACKET = 2
# Total timeout for command execution (must be greater than PING_COUNT * PING_TIMEOUT_PER_PACKET)
COMMAND_TIMEOUT = (PING_COUNT * PING_TIMEOUT_PER_PACKET) + 5

# --- FUNCTION FOR PINGING A SINGLE TARGET ---
def ping_target(target_name, target_data):
"""Performs a series of pings and returns statistics."""
ip = target_data['ip']

# Add the per-packet timeout option (-W 2) for greater reliability and -c for the number of packets
PING_COMMAND = ['ping', '-c', str(PING_COUNT), '-W', str(PING_TIMEOUT_PER_PACKET), ip]

latencies = []
loss = 0

try:
# Run the ping command. Use an extended timeout for the entire command.
result = subprocess.run( 
PING_COMMAND, 
capture_output=True, 
text=True, 
timeout=COMMAND_TIMEOUT 
) 

# Parse the ping output 

#1. Finding losses 
loss_line = [line for line in result.stdout.split('\n') if 'transmitted' in line] 
if loss_line: 
# Example: 3 packets transmitted, 2 received, 33% packet loss, time 2005ms 
parts = loss_line[0].split(', ') 
for part in parts: 
if 'loss' in part: 
# Extract the loss percentage 
loss_percent_str = part.split()[0].replace('%', '') 
loss_percent = float(loss_percent_str) 
received_count = PING_COUNT - int(PING_COUNT * loss_percent / 100)
loss = PING_COUNT - received_count

# 2. Finding the time (latency)
rtt_line = [line for line in result.stdout.split('\n') if 'min/avg/max' in line]
if rtt_line:
# Example: rtt min/avg/max/mdev = 44.130/45.289/46.853/1.121 ms
# Taking only the average value (avg)
avg_latency = float(rtt_line[0].split('=')[1].split('/')[1])
latencies.append(avg_latency)

# If the average time could not be found or all packets were lost,
# return "Infinity" and the full loss percentage. if not latencies or loss == PING_COUNT:
return float('inf'), 100.0, PING_COUNT, loss

return latencies[0], loss_percent, PING_COUNT, loss

except subprocess.TimeoutExpired:
# Overall command timeout
return float('inf'), 100.0, PING_COUNT, PING_COUNT
except Exception as e:
# Other errors (e.g., host unreachable)
# print(f"Error pinging {target_name}: {e}", file=sys.stderr)
return float('inf'), 100.0, PING_COUNT, PING_COUNT

# --- MAIN ANALYSIS FUNCTION ---
def run_geo_analyzer():
start_time = datetime.now()
results = {}

print("🌍 Launching the PING geo-analyzer...")
print(f" Checking {len(TARGETS)} global targets. Sending {PING_COUNT} packets to each target.")
print("=" * 80)

# 1. Performing pings
for name, data in TARGETS.items():
avg_latency, loss_percent, transmitted, lost = ping_target(name, data)

results[name] = {
'ip': data['ip'],
'location': data['location'],
'avg_latency': avg_latency,
'loss_percent': loss_percent,
'transmitted': transmitted,
'lost': lost
}

status = "✅ OK" if avg_latency != float('inf') else "❌ FAIL"
latency_str = f"{avg_latency:.2f} ms" if avg_latency != float('inf') else "TIMEOUT" 

print(f"[{st
