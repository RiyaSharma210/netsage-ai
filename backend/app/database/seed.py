import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "netsage.db")

LAB_CASES = [
    {
        "id": "CASE-VLAN-01",
        "title": "VLAN 30 Inter-VLAN Access Denied",
        "symptom": "Host on VLAN 30 cannot reach default gateway or ping outer subnets.",
        "topology_notes": "Core Switch SW-1 connected via Trunk to Gateway Router R1.",
        "device": "SW-1",
        "category": "VLAN",
        "severity": "high",
        "show_output": "SW-1# show vlan brief\n1 default active Fa0/1, Fa0/2\n10 Management active Fa0/3\n20 Sales active Fa0/4\n\nSW-1# show interfaces trunk\nPort Mode Encapsulation Status Native vlan\nFa0/24 on 802.1q trunking 1\n\nPort Vlans allowed on trunk\nFa0/24 1-20",
        "expected_fault": "VLAN 30 is missing from the switch database and trunk allowed list.",
        "expected_fix": "configure terminal\nvlan 30\n name Engineering\ninterface FastEthernet0/24\n switchport trunk allowed vlan add 30\nend",
        "ai_confidence": 0.95
    },
    {
        "id": "CASE-VLAN-02",
        "title": "Trunk Allowed List Missing Target VLAN",
        "symptom": "Hosts in VLAN 20 report total loss of connectivity across switches.",
        "topology_notes": "SW-1 to SW-2 direct trunk link on Gi0/1.",
        "device": "SW-1",
        "category": "VLAN",
        "severity": "medium",
        "show_output": "SW-1# show interfaces trunk\nPort Mode Encapsulation Status Native vlan\nGi0/1 on 802.1q trunking 1\n\nPort Vlans allowed on trunk\nGi0/1 1,10,30,40",
        "expected_fault": "VLAN 20 pruned from switchport trunk allowed vlan list.",
        "expected_fix": "configure terminal\ninterface GigabitEthernet0/1\n switchport trunk allowed vlan add 20\nend",
        "ai_confidence": 0.98
    },
    {
        "id": "CASE-VLAN-03",
        "title": "Native VLAN Mismatch Alert",
        "symptom": "CDP reporting %CDP-4-NATIVE_VLAN_MISMATCH warnings every 60 seconds.",
        "topology_notes": "SW-1 connected to SW-2 via trunk link.",
        "device": "SW-1",
        "category": "VLAN",
        "severity": "medium",
        "show_output": "SW-1# show interfaces trunk\nPort Mode Encapsulation Status Native vlan\nGi0/2 on 802.1q trunking 99\n\n%CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch discovered on GigabitEthernet0/2 (99), with SW-2 GigabitEthernet0/2 (1).",
        "expected_fault": "Native VLAN configured as 99 on SW-1 but remains default 1 on SW-2.",
        "expected_fix": "configure terminal\ninterface GigabitEthernet0/2\n switchport trunk native vlan 99\nend",
        "ai_confidence": 0.99
    },
    {
        "id": "CASE-VLAN-04",
        "title": "Uncreated VLAN Database Entry",
        "symptom": "Access port interface Fa0/5 assigned to VLAN 50 shows err-disabled or inactive status.",
        "topology_notes": "Access Layer Switch SW-3.",
        "device": "SW-3",
        "category": "VLAN",
        "severity": "low",
        "show_output": "SW-3# show vlan brief\n1 default active Fa0/1, Fa0/2\n10 HR active Fa0/3\n\nSW-3# show running-config interface Fa0/5\ninterface FastEthernet0/5\n switchport access vlan 50\n switchport mode access",
        "expected_fault": "VLAN 50 assigned to port but never created in VLAN database.",
        "expected_fix": "configure terminal\nvlan 50\n name Guest_Wi-Fi\nend",
        "ai_confidence": 0.96
    },
    {
        "id": "CASE-ROUT-01",
        "title": "Missing Default Static Route on Edge Router",
        "symptom": "Internal LAN nodes cannot reach public internet IPs (e.g. 8.8.8.8).",
        "topology_notes": "Edge Router R1 connected to ISP Gateway 203.0.113.1.",
        "device": "R1",
        "category": "Routing",
        "severity": "high",
        "show_output": "R1# show ip route\nCodes: C - connected, S - static, R - RIP, M - mobile, B - BGP\nGateway of last resort is not set\n\n 192.168.1.0/24 is variably subnetted, 1 subnets, 1 masks\nC 192.168.1.0/24 is directly connected, GigabitEthernet0/0/0\n 203.0.113.0/30 is subnetted, 1 subnets\nC 203.0.113.0/30 is directly connected, GigabitEthernet0/0/1",
        "expected_fault": "Gateway of last resort (default route 0.0.0.0/0) missing on R1.",
        "expected_fix": "configure terminal\nip route 0.0.0.0 0.0.0.0 203.0.113.1\nend",
        "ai_confidence": 0.97
    },
    {
        "id": "CASE-ROUT-02",
        "title": "OSPF Area Mismatch Between Core Routers",
        "symptom": "OSPF neighbor state stuck in INIT/DOWN between R1 and R2.",
        "topology_notes": "R1 and R2 connected directly via Gi0/0/0.",
        "device": "R1",
        "category": "Routing",
        "severity": "high",
        "show_output": "R1# show ip ospf neighbor\n(No neighbors listed)\n\nR1# show running-config | section router ospf\nrouter ospf 1\n router-id 1.1.1.1\n network 10.0.0.0 0.0.0.3 area 0\n\n%OSPF-4-ERRRCV: Received packet from 10.0.0.2, Area 1 mismatch from Area 0 on GigabitEthernet0/0/0",
        "expected_fault": "R1 configured in Area 0 while R2 interface configured in Area 1.",
        "expected_fix": "configure terminal\nrouter ospf 1\n no network 10.0.0.0 0.0.0.3 area 0\n network 10.0.0.0 0.0.0.3 area 1\nend",
        "ai_confidence": 0.98
    },
    {
        "id": "CASE-ROUT-03",
        "title": "Subnet Mask Misconfiguration on Subinterface",
        "symptom": "Inter-VLAN routing failing for VLAN 10 on Router-on-a-Stick setup.",
        "topology_notes": "Router R1 subinterface Gi0/0/0.10 for VLAN 10.",
        "device": "R1",
        "category": "Routing",
        "severity": "high",
        "show_output": "R1# show ip interface brief\nInterface IP-Address OK? Method Status Protocol\nGi0/0/0 unassigned YES unset up up\nGi0/0/0.10 192.168.10.1 YES manual up up\n\nR1# show running-config interface Gi0/0/0.10\ninterface GigabitEthernet0/0/0.10\n encapsulation dot1Q 10\n ip address 192.168.10.1 255.255.255.240",
        "expected_fault": "Subnet mask 255.255.255.240 (/28) configured instead of 255.255.255.0 (/24).",
        "expected_fix": "configure terminal\ninterface GigabitEthernet0/0/0.10\n ip address 192.168.10.1 255.255.255.0\nend",
        "ai_confidence": 0.94
    },
    {
        "id": "CASE-ROUT-04",
        "title": "Static Route Next-Hop Unreachable",
        "symptom": "Traffic destined to 172.16.0.0/16 is dropped at HQ Router.",
        "topology_notes": "HQ Router forwarding to Branch Router.",
        "device": "HQ-RTR",
        "category": "Routing",
        "severity": "medium",
        "show_output": "HQ-RTR# show ip route 172.16.0.0\n% Network not in table\n\nHQ-RTR# show running-config | include ip route\nip route 172.16.0.0 255.255.0.0 10.255.0.2\n\nHQ-RTR# show ip interface brief\nGi0/0/0 10.0.0.1 YES manual up up",
        "expected_fault": "Next-hop IP 10.255.0.2 in static route is not in any connected subnet range.",
        "expected_fix": "configure terminal\nno ip route 172.16.0.0 255.255.0.0 10.255.0.2\nip route 172.16.0.0 255.255.0.0 10.0.0.2\nend",
        "ai_confidence": 0.92
    },
    {
        "id": "CASE-DHCP-01",
        "title": "DHCP Pool IP Address Exhaustion",
        "symptom": "New workstations receiving APIPA addresses (169.254.x.x).",
        "topology_notes": "Central Cisco Router functioning as DHCP Server.",
        "device": "R1",
        "category": "DHCP",
        "severity": "high",
        "show_output": "R1# show ip dhcp pool LAN_POOL\nPool LAN_POOL :\n Utilization mark (high/low) : 100 / 0\n Subnet size between max : 254\n Total addresses : 254\n Leased addresses : 254\n Pending leases : 0\n Failed leases : 12\n\nSubnet 192.168.10.0 /24",
        "expected_fault": "DHCP pool LAN_POOL has 100% address utilization.",
        "expected_fix": "configure terminal\nip dhcp pool LAN_POOL\n network 192.168.10.0 255.255.252.0\nend",
        "ai_confidence": 0.96
    },
    {
        "id": "CASE-DHCP-02",
        "title": "Missing IP Helper-Address on Gateway",
        "symptom": "Clients on VLAN 20 do not receive DHCP configuration from central server 10.10.10.50.",
        "topology_notes": "Core L3 Switch acting as Default Gateway for VLAN 20.",
        "device": "SW-CORE",
        "category": "DHCP",
        "severity": "high",
        "show_output": "SW-CORE# show running-config interface vlan 20\ninterface Vlan20\n ip address 192.168.20.1 255.255.255.0\n ! No helper address configured\nend",
        "expected_fault": "Interface Vlan20 missing 'ip helper-address 10.10.10.50' to forward broadcast DHCPDISCOVER requests.",
        "expected_fix": "configure terminal\ninterface Vlan20\n ip helper-address 10.10.10.50\nend",
        "ai_confidence": 0.99
    },
    {
        "id": "CASE-DHCP-03",
        "title": "Excluded Address Overlap",
        "symptom": "IP conflict warnings reported on static gateway IP 192.168.1.1.",
        "topology_notes": "Local Cisco Router running DHCP Server.",
        "device": "R1",
        "category": "DHCP",
        "severity": "medium",
        "show_output": "R1# show ip dhcp binding\nIP address Client-ID/ Hardware address Lease expiration Type\n192.168.1.1 0100.1122.3344.55 Mar 15 2026 12:00 PM Automatic\n\nR1# show running-config | include ip dhcp excluded-address\n! No excluded addresses configured",
        "expected_fault": "Default gateway and static IPs missing from ip dhcp excluded-address configuration.",
        "expected_fix": "configure terminal\nip dhcp excluded-address 192.168.1.1 192.168.1.10\nend",
        "ai_confidence": 0.95
    },
    {
        "id": "CASE-DHCP-04",
        "title": "Wrong Default-Router IP in Scope",
        "symptom": "DHCP clients obtain IP address but cannot reach default gateway or remote networks.",
        "topology_notes": "Local Router DHCP Server for 192.168.30.0/24.",
        "device": "R1",
        "category": "DHCP",
        "severity": "high",
        "show_output": "R1# show ip dhcp pool SCOPE_30\nPool SCOPE_30 :\n Lease structure: 1 days 0 hours 0 mins\n Domain name : local.lab\n Default router : 192.168.30.254\n Subnet : 192.168.30.0 /24\n\nR1# show ip interface brief | include Vlan30\nVlan30 192.168.30.1 YES manual up up",
        "expected_fault": "Default-router configured as 192.168.30.254 instead of actual gateway IP 192.168.30.1.",
        "expected_fix": "configure terminal\nip dhcp pool SCOPE_30\n default-router 192.168.30.1\nend",
        "ai_confidence": 0.97
    },
    {
        "id": "CASE-DNS-01",
        "title": "Unreachable IP Domain Lookup Server",
        "symptom": "Router delays execution when entering invalid CLI commands, trying to resolve domain name.",
        "topology_notes": "Enterprise Edge Router R1.",
        "device": "R1",
        "category": "DNS",
        "severity": "low",
        "show_output": "R1# show running-config | include name-server\nip name-server 1.1.1.1\n\nR1# ping 1.1.1.1\nType escape sequence to abort.\nSending 5, 100-byte ICMP Echos to 1.1.1.1, timeout is 2 seconds:\n.....\nSuccess rate is 0 percent (0/5)",
        "expected_fault": "Configured DNS server 1.1.1.1 unreachable due to lack of Internet route.",
        "expected_fix": "configure terminal\nno ip name-server 1.1.1.1\nip name-server 8.8.8.8\nend",
        "ai_confidence": 0.91
    },
    {
        "id": "CASE-DNS-02",
        "title": "Missing IP Domain Lookup Enablement",
        "symptom": "Hostnames fail to resolve on local network clients.",
        "topology_notes": "Central DNS Server configured on Cisco IOS.",
        "device": "R1",
        "category": "DNS",
        "severity": "medium",
        "show_output": "R1# show running-config | include domain\nip domain name lab.local\nno ip domain lookup",
        "expected_fault": "'no ip domain lookup' prevents router from resolving hostnames via DNS.",
        "expected_fix": "configure terminal\nip domain lookup\nend",
        "ai_confidence": 0.98
    },
    {
        "id": "CASE-DNS-03",
        "title": "DNS Service Disabled on Cisco Server",
        "symptom": "Router configured as DNS server fails to respond to client DNS requests on UDP 53.",
        "topology_notes": "Branch Router acting as local DNS forwarder.",
        "device": "BR-RTR",
        "category": "DNS",
        "severity": "medium",
        "show_output": "BR-RTR# show running-config | include dns\nip name-server 8.8.8.8\n! ip dns server is absent",
        "expected_fault": "'ip dns server' command is missing.",
        "expected_fix": "configure terminal\nip dns server\nend",
        "ai_confidence": 0.96
    },
    {
        "id": "CASE-ACL-01",
        "title": "Implicit Deny Blocking Outbound Web Traffic",
        "symptom": "Internal hosts cannot connect to HTTP/HTTPS websites.",
        "topology_notes": "Edge Router R1 interface Gi0/0/1 outbound ACL.",
        "device": "R1",
        "category": "ACL",
        "severity": "high",
        "show_output": "R1# show ip access-lists OUTBOUND_FILTER\nExtended IP access list OUTBOUND_FILTER\n 10 permit tcp 192.168.1.0 0.0.0.255 any eq 22\n 20 permit icmp any any\n ! Default implicit deny ip any any active",
        "expected_fault": "ACL lacks permit statements for TCP ports 80 (HTTP) and 443 (HTTPS).",
        "expected_fix": "configure terminal\nip access-list extended OUTBOUND_FILTER\n 30 permit tcp 192.168.1.0 0.0.0.255 any eq www\n 40 permit tcp 192.168.1.0 0.0.0.255 any eq 443\nend",
        "ai_confidence": 0.97
    },
    {
        "id": "CASE-ACL-02",
        "title": "Standard ACL Applied Inbound on Wrong Interface",
        "symptom": "All internal traffic blocked at router LAN interface.",
        "topology_notes": "R1 LAN Interface Gi0/0/0.",
        "device": "R1",
        "category": "ACL",
        "severity": "high",
        "show_output": "R1# show ip interface Gi0/0/0 | include access list\n Inbound access list is 10\n Outbound access list is not set\n\nR1# show access-lists 10\nStandard IP access list 10\n 10 permit 10.0.0.0 0.255.255.255",
        "expected_fault": "Standard ACL 10 applied inbound on LAN interface matching 10.0.0.0/8, dropping 192.168.1.0/24 LAN subnet.",
        "expected_fix": "configure terminal\ninterface GigabitEthernet0/0/0\n no ip access-group 10 in\nend",
        "ai_confidence": 0.94
    },
    {
        "id": "CASE-ACL-03",
        "title": "Incorrect Wildcard Mask in Access List",
        "symptom": "ACL permits unintended IP addresses in subnet 192.168.16.0/20.",
        "topology_notes": "Core Router Access Control filtering.",
        "device": "R1",
        "category": "ACL",
        "severity": "medium",
        "show_output": "R1# show ip access-lists SECURE_ACCESS\nExtended IP access list SECURE_ACCESS\n 10 permit ip 192.168.16.0 0.0.255.255 any",
        "expected_fault": "Wildcard mask 0.0.255.255 matches /16 range instead of /24 range (0.0.0.255).",
        "expected_fix": "configure terminal\nip access-list extended SECURE_ACCESS\n no 10\n 10 permit ip 192.168.16.0 0.0.0.255 any\nend",
        "ai_confidence": 0.95
    },
    {
        "id": "CASE-ACL-04",
        "title": "Telnet/SSH VTY Line Access Blocked",
        "symptom": "Network administrator unable to SSH into router remotely.",
        "topology_notes": "R1 VTY lines 0 through 4.",
        "device": "R1",
        "category": "ACL",
        "severity": "high",
        "show_output": "R1# show running-config | section line vty\nline vty 0 4\n access-class 50 in\n transport input ssh\n\nR1# show access-lists 50\nStandard IP access list 50\n 10 permit 10.1.1.5",
        "expected_fault": "VTY access-class 50 blocks admin IP 192.168.1.100.",
        "expected_fix": "configure terminal\naccess-list 50 permit 192.168.1.100\nend",
        "ai_confidence": 0.98
    },
    {
        "id": "CASE-NAT-01",
        "title": "Missing 'ip nat inside' Command on LAN Interface",
        "symptom": "Internal host traffic reaching WAN interface without translation; dropped by ISP.",
        "topology_notes": "NAT Edge Router R1.",
        "device": "R1",
        "category": "NAT",
        "severity": "high",
        "show_output": "R1# show ip nat statistics\nTotal active translations: 0\nOutside interface: GigabitEthernet0/0/1\nInside interface: (none)\n\nR1# show running-config interface Gi0/0/0\ninterface GigabitEthernet0/0/0\n ip address 192.168.1.1 255.255.255.0",
        "expected_fault": "GigabitEthernet0/0/0 lacks 'ip nat inside' configuration.",
        "expected_fix": "configure terminal\ninterface GigabitEthernet0/0/0\n ip nat inside\nend",
        "ai_confidence": 0.99
    },
    {
        "id": "CASE-NAT-02",
        "title": "NAT ACL Denies LAN Source Subnet",
        "symptom": "NAT overload (PAT) not functioning for LAN 192.168.20.0/24.",
        "topology_notes": "R1 Dynamic NAT overload setup.",
        "device": "R1",
        "category": "NAT",
        "severity": "high",
        "show_output": "R1# show running-config | include ip nat inside source\nip nat inside source list 100 interface GigabitEthernet0/0/1 overload\n\nR1# show ip access-lists 100\nExtended IP access list 100\n 10 permit ip 192.168.10.0 0.0.0.255 any",
        "expected_fault": "ACL 100 permits 192.168.10.0/24 but omits 192.168.20.0/24.",
        "expected_fix": "configure terminal\nip access-list extended 100\n 20 permit ip 192.168.20.0 0.0.0.255 any\nend",
        "ai_confidence": 0.96
    },
    {
        "id": "CASE-NAT-03",
        "title": "Pool Exhaustion on Static One-to-One NAT",
        "symptom": "External clients unable to access public web server.",
        "topology_notes": "Border Router Static NAT translation.",
        "device": "R1",
        "category": "NAT",
        "severity": "high",
        "show_output": "R1# show ip nat translations\nPro Inside global Inside local Outside local Outside global\n--- 203.0.113.10 10.0.0.5 --- ---\n\nR1# show running-config | include ip nat inside source static\nip nat inside source static 10.0.0.5 203.0.113.10",
        "expected_fault": "Static NAT translation points to decommissioned IP 10.0.0.5 instead of server IP 10.0.0.50.",
        "expected_fix": "configure terminal\nno ip nat inside source static 10.0.0.5 203.0.113.10\nip nat inside source static 10.0.0.50 203.0.113.10\nend",
        "ai_confidence": 0.93
    },
    {
        "id": "CASE-WLAN-01",
        "title": "WPA2 Pre-Shared Key Mismatch",
        "symptom": "Wireless clients fail to authenticate to Corporate SSID.",
        "topology_notes": "Cisco WLC / Autonomous AP.",
        "device": "AP-1",
        "category": "Wireless",
        "severity": "medium",
        "show_output": "AP-1# show dot11 associations\n(No active client associations on Radio 0)\n\nAP-1# show running-config | section dot11 ssid Corporate\ndot11 ssid Corporate\n authentication open\n authentication key-management wpa version 2\n wpa-psk ascii 0 CiscoSecret2026!",
        "expected_fault": "WPA2 Pre-shared key configured on AP does not match client deployment profile.",
        "expected_fix": "configure terminal\ndot11 ssid Corporate\n wpa-psk ascii 0 CiscoLabKey123!\nend",
        "ai_confidence": 0.92
    },
    {
        "id": "CASE-WLAN-02",
        "title": "Wireless Management VLAN Mapping Error",
        "symptom": "Access Points cannot obtain IP addresses from DHCP WLC management scope.",
        "topology_notes": "Access Switch Gi0/10 connected to AP-1.",
        "device": "SW-1",
        "category": "Wireless",
        "severity": "high",
        "show_output": "SW-1# show running-config interface Gi0/10\ninterface GigabitEthernet0/10\n switchport access vlan 1\n switchport mode access",
        "expected_fault": "Switchport configured in VLAN 1 instead of Wireless AP Management VLAN 40.",
        "expected_fix": "configure terminal\ninterface GigabitEthernet0/10\n switchport access vlan 40\nend",
        "ai_confidence": 0.97
    },
    {
        "id": "CASE-WLAN-03",
        "title": "Access Point LWAPP/CAPWAP Joining Failure",
        "symptom": "Lightweight AP stuck in Discovery phase loop.",
        "topology_notes": "CAPWAP AP connecting to WLC at 10.10.10.10.",
        "device": "AP-2",
        "category": "Wireless",
        "severity": "high",
        "show_output": "AP-2# show capwap client status\nLWAPP status : DISCOVERING\nTranslating \"CISCO-CAPWAP-CONTROLLER.local.lab\"...failed\nDHCP Option 43 : Not Received",
        "expected_fault": "DHCP Option 43 or DNS entry missing to inform AP of WLC management IP.",
        "expected_fix": "configure terminal\nip dhcp pool AP_POOL\n option 43 ip 10.10.10.10\nend",
        "ai_confidence": 0.98
    },
    {
        "id": "CASE-INT-01",
        "title": "Administratively Down Link on Gateway Interface",
        "symptom": "Gateway interface unreachable; show ip interface brief displays 'administratively down'.",
        "topology_notes": "R1 Core Interface Gi0/0/0.",
        "device": "R1",
        "category": "Interface",
        "severity": "high",
        "show_output": "R1# show ip interface brief\nInterface IP-Address OK? Method Status Protocol\nGigabitEthernet0/0/0 192.168.1.1 YES manual administratively down down",
        "expected_fault": "Interface disabled via shutdown command.",
        "expected_fix": "configure terminal\ninterface GigabitEthernet0/0/0\n no shutdown\nend",
        "ai_confidence": 0.99
    },
    {
        "id": "CASE-INT-02",
        "title": "Duplex Mismatch Causing Heavy Late Collisions",
        "symptom": "Severe throughput degradation and packet drop on switch-to-switch link.",
        "topology_notes": "SW-1 Gi0/1 connected to SW-2 Gi0/1.",
        "device": "SW-1",
        "category": "Interface",
        "severity": "medium",
        "show_output": "SW-1# show interfaces Gi0/1\nGigabitEthernet0/1 is up, line protocol is up\n Half-duplex, 100Mb/s, link type is auto\n 452134 late collisions, 12049 runts, 0 CRC errors",
        "expected_fault": "Interface forced to Half-duplex while remote peer is Full-duplex.",
        "expected_fix": "configure terminal\ninterface GigabitEthernet0/1\n duplex auto\n speed auto\nend",
        "ai_confidence": 0.96
    },
    {
        "id": "CASE-GW-01",
        "title": "Host Static Default Gateway Subnet Mismatch",
        "symptom": "Host IP 192.168.10.50 cannot reach default gateway 192.168.20.1.",
        "topology_notes": "Host connected to SW-1 Access Port in VLAN 10.",
        "device": "HOST-PC1",
        "category": "Routing",
        "severity": "medium",
        "show_output": "HOST-PC1> ipconfig\nIPv4 Address. . . . . . . . . . . : 192.168.10.50\nSubnet Mask . . . . . . . . . . . : 255.255.255.0\nDefault Gateway . . . . . . . . . : 192.168.20.1",
        "expected_fault": "Default Gateway configured in wrong IP subnet.",
        "expected_fix": "Host IP Configuration:\nSet Default Gateway to 192.168.10.1",
        "ai_confidence": 0.98
    },
    {
        "id": "CASE-MULTI-01",
        "title": "Layer 2 Trunk Down & Layer 3 Subinterface IP Error",
        "symptom": "Inter-VLAN routing failure combined with trunk negotiation failure.",
        "topology_notes": "R1 connected to SW-1 via trunk.",
        "device": "SW-1",
        "category": "VLAN",
        "severity": "high",
        "show_output": "SW-1# show interfaces trunk\n(No active trunk interfaces)\n\nSW-1# show running-config interface Gi0/1\ninterface GigabitEthernet0/1\n switchport mode dynamic auto",
        "expected_fault": "Trunk port set to dynamic auto on both sides resulting in access mode default.",
        "expected_fix": "configure terminal\ninterface GigabitEthernet0/1\n switchport mode trunk\nend",
        "ai_confidence": 0.95
    },
    {
        "id": "CASE-MULTI-02",
        "title": "NAT PAT Failure Combined with Inbound ACL Block",
        "symptom": "Outbound web access failing due to multiple security and NAT policy errors.",
        "topology_notes": "Border Router R1.",
        "device": "R1",
        "category": "NAT",
        "severity": "high",
        "show_output": "R1# show ip access-lists 101\nExtended IP access list 101\n 10 deny ip 192.168.1.0 0.0.0.255 any\n\nR1# show ip nat statistics\nTotal active translations: 0",
        "expected_fault": "NAT ACL 101 contains explicit deny statement blocking LAN subnet before permit rule.",
        "expected_fix": "configure terminal\nip access-list extended 101\n no 10\n 10 permit ip 192.168.1.0 0.0.0.255 any\nend",
        "ai_confidence": 0.97
    }
]

def seed_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        symptom TEXT NOT NULL,
        topology_notes TEXT,
        device TEXT NOT NULL,
        show_output TEXT NOT NULL,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        expected_fault TEXT,
        expected_fix TEXT,
        ai_confidence REAL,
        status TEXT DEFAULT 'PENDING'
    )
    """)

    cursor.execute("DELETE FROM cases")

    for case in LAB_CASES:
        cursor.execute("""
        INSERT INTO cases (id, title, symptom, topology_notes, device, show_output, category, severity, expected_fault, expected_fix, ai_confidence, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
        """, (
            case["id"],
            case["title"],
            case["symptom"],
            case["topology_notes"],
            case["device"],
            case["show_output"],
            case["category"],
            case["severity"],
            case["expected_fault"],
            case["expected_fix"],
            case["ai_confidence"]
        ))

    conn.commit()
    conn.close()
    print(f"Successfully seeded {len(LAB_CASES)} Cisco Lab Cases into {DB_PATH}")

if __name__ == "__main__":
    seed_db()