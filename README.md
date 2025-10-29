🌐 Geo Ping Analyzer

This Python script (geo_ping_analyzer.py) is designed to determine the approximate geographic location of your network connection (IP address) by measuring the latency to various global DNS servers.

The lower the latency (ping), the closer the server is physically to your current location.

🚀 How does it work?

Global Coverage: The script sends 3 ping packets to each of 10+ globally distributed IP addresses covering North America, South America, Europe, Asia, and Oceania.

Latency Measurement: The average response time (RTT) and packet loss percentage for each target are recorded.

Analysis: The script identifies the target with the lowest latency.

Conclusion: Based on the closest target and its response time, a conclusion is made about your approximate location (continent/region).

🛠️ Running the Script

Make sure you have Python installed (Python 3 is recommended).

Execution

To run the analyzer, run the following command:

python3 geo_ping_analyzer.py

Example Output

🌍 Running the PING geo-analyzer...
Checking 10 global targets. Sending 3 packets to each target.
== ... Location: Virginia/California, USA (North America)
[✅ OK] Cloudflare_EU: 45.75 ms | Loss: 0.0% (0/3) | Location: Frankfurt/London, Germany/United Kingdom (Europe)
...
[✅ OK] OpenDNS_ZA: 320.10 ms | Loss: 0.0% (0/3) | Location: Johannesburg, South Africa (Africa)
= ... ====================================================================================

⭐ GEOGRAPHICAL LOCATION ESTIMATION BY PING
================================================================================================
Based on network latency analysis, the CLOSEST point to you is:
-> TARGET: Cloudflare_EU (1.1.1.1)
-> LOCATION: Frankfurt/London Germany/UK (Europe)
-> AVERAGE PING: 45.75 ms
-> LOSS: 0.0%

✅ CONCLUSION:
Your network connection is likely in the same region (or continent) as Frankfurt/London, Germany/UK (Europe). This is confirmed by the very low latency (RTT).
======================================================================================

⚙️ Configuration (geo_ping_analyzer.py)

You can configure the following parameters at the beginning of the geo_ping_analyzer.py file:

Parameter

Description

Default value

TARGETS

Dictionary with global targets (IP and location). Expanded for worldwide coverage.

10+ targets on all continents

PING_COUNT

Number of packets sent to each target.

3

PING_TIMEOUT_PER_PACKET

Timeout for waiting for a response to one packet (in seconds).

2
