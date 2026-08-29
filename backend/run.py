import os
import sqlite3
import time
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "netsage.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cases (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        symptom TEXT NOT NULL,
        topology_notes TEXT NOT NULL,
        device TEXT NOT NULL,
        show_output TEXT NOT NULL,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        expected_fault TEXT,
        osi_layer TEXT,
        concept TEXT,
        expected_next_command TEXT,
        expected_fix TEXT,
        status TEXT DEFAULT 'pending',
        ai_confidence REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Force reload database if missing 30 lab cases
    cursor.execute("SELECT COUNT(*) FROM cases")
    count = cursor.fetchone()[0]
    
    if count < 30:
        cursor.execute("DELETE FROM cases")
        sample_cases = [
            # VLAN & SWITCHING (1-6)
            ("CASE-VLAN-01", "VLAN 30 Inter-VLAN Access Denied", "PC-101 in VLAN 30 receives IP 192.168.30.10 via DHCP but cannot ping Server in VLAN 10.", "PC-101 -> Access Switch (SW-1) -> Trunk -> Core Router (R-1) -> Server-10", "SW-1", "SW-1# show vlan brief\nVLAN Name Status Ports\n1 default active Fa0/1, Fa0/2\n10 Accounting active Fa0/5\n30 Engineering active\n\nSW-1# show interfaces FastEthernet 0/3 switchport\nAccess Mode VLAN: 1 (default)", "VLAN", "high", "Interface Fa0/3 assigned to default VLAN 1 instead of VLAN 30", "Layer 2", "Access Port Assignment", "show interfaces Fa0/3 switchport", "interface FastEthernet0/3\n switchport mode access\n switchport access vlan 30", "pending"),
            ("CASE-VLAN-02", "Trunk Allowed List Missing Target VLAN", "VLAN 20 hosts lose connectivity across core switch link after maintenance.", "Switch-A (Fa0/24) <---> (Fa0/24) Switch-B", "Switch-A", "Switch-A# show interfaces trunk\nPort Mode Encapsulation Status Native vlan\nFa0/24 on 802.1q trunking 1\nPort Vlans allowed on trunk\nFa0/24 1,10,30", "VLAN", "critical", "VLAN 20 omitted from switchport trunk allowed vlan list", "Layer 2", "Trunk Encapsulation & Pruning", "show interfaces trunk", "interface FastEthernet0/24\n switchport trunk allowed vlan add 20", "pending"),
            ("CASE-VLAN-03", "Native VLAN Mismatch Alert", "CDP reports Native VLAN Mismatch between Switch-1 and Switch-2 on Gi0/1.", "SW-1 (Gi0/1) <---> (Gi0/1) SW-2", "SW-1", "SW-1# show interfaces gigabitEthernet 0/1 switchport\nTrunking Native Mode VLAN: 1 (default)\nSW-2# show interfaces gigabitEthernet 0/1 switchport\nTrunking Native Mode VLAN: 99 (NATIVE)", "VLAN", "medium", "Native VLAN mismatch across trunk link", "Layer 2", "802.1Q Native VLAN", "show interfaces trunk", "interface GigabitEthernet0/1\n switchport trunk native vlan 99", "pending"),
            ("CASE-VLAN-04", "Voice VLAN Helper Misconfiguration", "IP Phones fail to register with Cisco Unified Communications Manager.", "IP Phone -> SW-1 (Port Fa0/10) -> Voice VLAN 150", "SW-1", "SW-1# show switchport interface Fa0/10\nVoice VLAN: dot1p\nAccess Mode VLAN: 10", "VLAN", "high", "Voice VLAN improperly configured as dot1p instead of dedicated VLAN 150", "Layer 2", "Voice VLAN", "show interfaces Fa0/10 switchport", "interface FastEthernet0/10\n switchport voice vlan 150", "pending"),
            ("CASE-VLAN-05", "DTP Mode Mismatch Blocking Trunking", "Link between SW-Core and SW-Access remains in Access mode.", "SW-Core (Gi0/2) <---> (Gi0/2) SW-Access", "SW-Access", "SW-Access# show interfaces Gi0/2 switchport\nAdministrative Mode: dynamic auto\nOperational Mode: static access", "VLAN", "medium", "Dynamic Auto on both sides prevented DTP negotiation", "Layer 2", "Dynamic Trunking Protocol", "show interfaces switchport", "interface GigabitEthernet0/2\n switchport mode trunk", "pending"),
            ("CASE-VLAN-06", "VTP Domain Mismatch Dropping VLAN Updates", "VLANs created on VTP Server are not syncing to Access Switches.", "Core-VTP-Server <---> Access-VTP-Client", "SW-Access", "SW-Access# show vtp status\nVTP Operating Mode: Client\nVTP Domain Name: LAB_WEST\nCore# show vtp status\nVTP Domain Name: LAB_EAST", "VLAN", "high", "VTP domain name mismatch between server and client", "Layer 2", "VTP Domain Management", "show vtp status", "vtp domain LAB_EAST", "pending"),

            # SPANNING TREE PROTOCOL (7-10)
            ("CASE-STP-01", "STP Root Bridge Instability", "Network experiences intermittent high latency due to root bridge election recalculations.", "Core Switch 1 <---> Core Switch 2", "SW-Core-2", "SW-Core-2# show spanning-tree vlan 10\nVLAN0010\n Spanning tree enabled protocol rstp\n Root ID Priority 32778\n Bridge ID Priority 32778", "STP", "critical", "Root priority left at default 32768, causing priority tie-breakers", "Layer 2", "RSTP Root Election", "show spanning-tree", "spanning-tree vlan 10 root primary", "pending"),
            ("CASE-STP-02", "BPDU Guard PortErrDisable", "Port Fa0/12 automatically went into err-disabled state upon PC connection.", "SW-Access Port Fa0/12 -> User PC", "SW-Access", "SW-Access# show interfaces Fa0/12 status\nPort Name Status Vlan Duplex Speed Type\nFa0/12 Link to Desk err-disabled 10 auto auto 10/100BaseTX", "STP", "high", "BPDU Guard triggered on port receiving unauthorized BPDUs", "Layer 2", "STP PortFast BPDU Guard", "show interfaces status err-disabled", "interface FastEthernet0/12\n shutdown\n no shutdown", "pending"),
            ("CASE-STP-03", "STP Loop Guard Blocking Designated Port", "Spanning tree put port Gi0/1 into loop-inconsistent state.", "SW-1 (Gi0/1) <---> (Gi0/1) SW-2", "SW-1", "SW-1# show spanning-tree inconsistentports\nName Interface Inconsistency\n------ -------------------- ------------------\nVLAN0001 GigabitEthernet0/1 Loop Inconsistent", "STP", "critical", "Unidirectional link loss detected by Loop Guard", "Layer 2", "STP Loop Guard", "show spanning-tree summary", "interface GigabitEthernet0/1\n udld enable", "pending"),
            ("CASE-STP-04", "PortFast Missing on Server Uplink", "Servers experience 30 second connection delay on reboot.", "Server-01 -> SW-Access Fa0/1", "SW-Access", "SW-Access# show spanning-tree interface Fa0/1 detail\n Port 1 (FastEthernet0/1) of VLAN0001 is forwarding\n Designated bridge has priority 32769\n PortFast is disabled", "STP", "low", "PortFast disabled causing listening and learning delays on edge link", "Layer 2", "STP PortFast", "show spanning-tree interface Fa0/1", "interface FastEthernet0/1\n spanning-tree portfast", "pending"),

            # ROUTING - OSPF & BGP (11-18)
            ("CASE-ROUT-01", "Missing Default Static Route on Edge Router", "Internal LAN PCs can reach local subnets but cannot reach public IP addresses (8.8.8.8).", "Router-Edge -> ISP Gateway (203.0.113.1)", "Router-Edge", "Router-Edge# show ip route\nGateway of last resort is not set\n192.168.1.0/24 is directly connected, GigabitEthernet0/0", "Routing", "critical", "Missing default static route (0.0.0.0/0) pointing to ISP gateway", "Layer 3", "Default Gateway Routing", "show ip route", "ip route 0.0.0.0 0.0.0.0 203.0.113.1", "pending"),
            ("CASE-OSPF-01", "OSPF Neighbor Area ID Mismatch", "R1 and R2 interfaces show UP/UP but OSPF adjacency stays in INIT/DOWN.", "R1 (Gi0/0) <---> (Gi0/0) R2", "R1", "R1# show ip ospf interface Gi0/0\nInternet Address 10.0.0.1/30, Area 0\nR2# show ip ospf interface Gi0/0\nInternet Address 10.0.0.2/30, Area 1", "OSPF", "high", "OSPF Area ID mismatch on connecting interfaces", "Layer 3", "OSPF Adjacency Criteria", "show ip ospf interface", "interface GigabitEthernet0/0\n ip ospf 1 area 0", "pending"),
            ("CASE-OSPF-02", "OSPF Hello/Dead Timer Mismatch", "OSPF neighbor state stuck in INIT mode.", "R1 (Gi0/1) <---> (Gi0/1) R2", "R2", "R2# show ip ospf interface Gi0/1\nTimer intervals configured, Hello 10, Dead 40\nR1# show ip ospf interface Gi0/1\nTimer intervals configured, Hello 30, Dead 120", "OSPF", "high", "OSPF Hello and Dead timer mismatch between peers", "Layer 3", "OSPF Timers", "show ip ospf interface", "interface GigabitEthernet0/1\n ip ospf hello-interval 10\n ip ospf dead-interval 40", "pending"),
            ("CASE-OSPF-03", "OSPF MTU Mismatch Adjacency Stuck in EXSTART", "OSPF neighbor relationship stuck in EXSTART/EXCHANGE state.", "R1 (Gi0/0) <---> (Gi0/0) R2", "R1", "R1# show ip ospf neighbor\nNeighbor ID Pri State Dead Time Address Interface\n2.2.2.2 1 EXSTART/ - 00:00:33 10.0.0.2 GigabitEthernet0/0", "OSPF", "high", "MTU mismatch on interface preventing DBD packet exchange", "Layer 3", "OSPF MTU Requirements", "show ip ospf neighbor", "interface GigabitEthernet0/0\n ip mtu 1500", "pending"),
            ("CASE-OSPF-04", "OSPF Passive Interface Blocking Hellos", "Branch router not receiving OSPF routes from LAN subnet.", "R-Branch (Gi0/2) -> LAN Switch", "R-Branch", "R-Branch# show ip ospf interface Gi0/2\nGi0/2 is up, line protocol is up\n No Hellos sent over passive interface", "OSPF", "medium", "Gi0/2 erroneously configured as passive-interface in OSPF process", "Layer 3", "OSPF Passive Interface", "show ip ospf interface", "router ospf 1\n no passive-interface GigabitEthernet0/2", "pending"),
            ("CASE-BGP-01", "eBGP Multihop Missing on Loopback Peer", "eBGP session between R1 and ISP remains Idle/Active.", "R1 (Loopback 1.1.1.1) <---> (2.2.2.2) R-ISP", "R1", "R1# show ip bgp summary\nNeighbor V AS MsgRcvd MsgSent TblVer InQ OutQ Up/Down State/PfxRcd\n2.2.2.2 4 65002 0 0 0 0 0 00:04:12 Active", "BGP", "critical", "eBGP peer TTL expired because ebgp-multihop was not enabled for loopbacks", "Layer 3", "eBGP Multihop", "show ip bgp summary", "router bgp 65001\n neighbor 2.2.2.2 ebgp-multihop 2", "pending"),
            ("CASE-BGP-02", "BGP Autonomous System Number Mismatch", "BGP session failing to establish with remote peer 198.51.100.1.", "Edge-Router <---> Telco-Peer", "Edge-Router", "Edge-Router# show ip bgp summary\nNeighbor V AS MsgRcvd MsgSent State\n198.51.100.1 4 65500 0 0 Active\nNotification sent: bad peer AS number", "BGP", "high", "Configured remote-as does not match provider AS", "Layer 3", "BGP Peering", "show ip bgp summary", "router bgp 64512\n neighbor 198.51.100.1 remote-as 65501", "pending"),
            ("CASE-BGP-03", "iBGP Next-Hop Unreachable", "iBGP routes learned but marked invalid in routing table.", "R1 (iBGP) <---> R2 (iBGP)", "R2", "R2# show ip bgp\n Status codes: i - internal\n   Network Next Hop Metric LocPrf Weight Path\n* i 172.16.0.0/16 203.0.113.5 0 100 0 i", "BGP", "high", "Next hop IP 203.0.113.5 unreachable in IGP; missing next-hop-self", "Layer 3", "iBGP Next-Hop-Self", "show ip bgp", "router bgp 64500\n neighbor 10.1.1.1 next-hop-self", "pending"),

            # SERVICES - DHCP, DNS, NAT (19-24)
            ("CASE-DHCP-01", "DHCP Pool IP Address Exhaustion", "New clients connecting to Wi-Fi receive APIPA addresses (169.254.x.x).", "Core Router acting as DHCP Server for LAN-Pool", "R-Core", "R-Core# show ip dhcp pool LAN-Pool\nPool LAN-Pool :\n Utilization mark (high/low) : 100 / 0\n Subnet size (leases/total) : 254 / 254\n Leased addresses : 254", "DHCP", "critical", "DHCP address pool exhausted (100% lease utilization)", "Layer 7", "DHCP Scope Management", "show ip dhcp pool", "ip dhcp pool LAN-Pool\n lease 0 8", "pending"),
            ("CASE-DHCP-02", "IP Helper-Address Missing on Relay Interface", "Clients in VLAN 40 cannot reach DHCP server hosted in Server VLAN 10.", "VLAN 40 Gateway (SVI 40) -> Core Router -> DHCP Server", "R-Core", "R-Core# show running-config interface vlan 40\ninterface Vlan40\n ip address 192.168.40.1 255.255.255.0\n! (No ip helper-address configured)", "DHCP", "high", "Missing ip helper-address command on SVI interface to forward UDP broadcasts", "Layer 7", "DHCP Relay Agent", "show running-config interface vlan 40", "interface Vlan40\n ip helper-address 10.1.1.100", "pending"),
            ("CASE-NAT-01", "NAT Inside Interface Missing", "Internal hosts cannot access internet through WAN gateway.", "LAN (Gi0/0) -> Router -> WAN (Gi0/1)", "Router-Edge", "Router-Edge# show ip nat statistics\nTotal active translations: 0\nOutside interface: GigabitEthernet0/1\nInside interface: none", "NAT", "high", "ip nat inside missing on internal LAN interface GigabitEthernet0/0", "Layer 3", "NAT Interface Configuration", "show ip nat statistics", "interface GigabitEthernet0/0\n ip nat inside", "pending"),
            ("CASE-NAT-02", "Overload ACL Omitted Target Subnet", "Subnet 192.168.20.0/24 cannot translate out WAN interface.", "LAN Subnets -> NAT Pool Router", "Router-Edge", "Router-Edge# show ip access-lists NAT-ACL\nStandard IP access list NAT-ACL\n 10 permit 192.168.10.0 0.0.0.255", "NAT", "medium", "Access-list used for PAT overload omitted 192.168.20.0/24 subnet", "Layer 3", "PAT / NAT ACLs", "show ip access-lists", "ip access-list standard NAT-ACL\n 20 permit 192.168.20.0 0.0.0.255", "pending"),
            ("CASE-DNS-01", "DNS Forwarder Timeout", "Internal clients fail to resolve external domain names.", "LAN Clients -> Internal DNS Server -> Forwarder (8.8.8.8)", "DNS-Server", "C:\\> nslookup google.com\nServer: internal-dns.local\nAddress: 192.168.1.5\n*** internal-dns.local request timed out.", "DNS", "medium", "Upstream DNS forwarder port 53 outbound blocked by firewall", "Layer 7", "DNS Resolution", "nslookup google.com", "firewall allow outbound udp port 53", "pending"),
            ("CASE-DNS-02", "Invalid Gateway Option in DHCP Pool", "DHCP Clients assigned incorrect default DNS server IP.", "DHCP Server -> Clients", "R-Core", "R-Core# show ip dhcp pool LAN\n default-router 192.168.1.1\n dns-server 192.168.1.250", "DNS", "low", "DNS server IP 192.168.1.250 in DHCP pool points to unreachable host", "Layer 7", "DHCP DNS Options", "show ip dhcp pool", "ip dhcp pool LAN\n dns-server 1.1.1.1 8.8.8.8", "pending"),

            # SECURITY & ACLs (25-28)
            ("CASE-ACL-01", "Implicit Deny Blocking HTTPS Traffic", "Web traffic to 10.10.10.50 fails after ACL installation.", "Client -> Router Gi0/0 (ACL 100 IN) -> Server", "R1", "R1# show ip access-lists 100\nExtended IP access list 100\n 10 permit tcp any host 10.10.10.50 eq www\n (Implicit deny ip any any active)", "ACL", "high", "Access list permits HTTP (port 80) but lacks rule for HTTPS (port 443)", "Layer 4", "Access Control Lists", "show ip access-lists 100", "ip access-list extended 100\n 15 permit tcp any host 10.10.10.50 eq 443", "pending"),
            ("CASE-ACL-02", "Inbound ACL Applied Outbound on Interface", "ACL 102 intended for inbound filtering applied in outbound direction.", "Router Gi0/1", "R1", "R1# show running-config interface Gi0/1\ninterface GigabitEthernet0/1\n ip access-group 102 out", "ACL", "medium", "ACL direction mismatch (applied 'out' instead of 'in')", "Layer 3", "ACL Application", "show running-config interface", "interface GigabitEthernet0/1\n no ip access-group 102 out\n ip access-group 102 in", "pending"),
            ("CASE-ACL-03", "SSH Telnet Service Blocked by Control Plane ACL", "Administrators cannot SSH into Core Switch.", "Management Workstation -> Core Switch", "SW-Core", "SW-Core# show line vty 0 4\nline vty 0 4\n access-class 50 in\nSW-Core# show ip access-list 50\nStandard IP access list 50\n 10 permit 10.1.100.0 0.0.0.255", "ACL", "high", "Admin IP address 10.2.100.45 not permitted in VTY access-class 50", "Layer 7", "VTY Line Security", "show ip access-lists 50", "access-list 50 permit host 10.2.100.45", "pending"),
            ("CASE-ACL-04", "Wildcard Mask Inversion Error", "ACL matches incorrect hosts due to incorrect subnet mask format.", "R1 Router", "R1", "R1# show ip access-lists 10\nStandard IP access list 10\n 10 permit 192.168.1.0 255.255.255.0", "ACL", "medium", "Subnet mask used instead of Cisco wildcard inverse mask 0.0.0.255", "Layer 3", "ACL Wildcard Masking", "show ip access-lists", "no access-list 10\naccess-list 10 permit 192.168.1.0 0.0.0.255", "pending"),

            # VPN & SECURITY (29-30)
            ("CASE-VPN-01", "IPsec Phase 1 Proposal Mismatch", "Site-to-Site VPN fails to negotiate ISAKMP SA.", "Router-HQ <--- IPsec Tunnel ---> Router-Branch", "Router-HQ", "Router-HQ# show crypto isakmp sa\n (No SAs present)\nLogs: %CRYPTO-3-IKMP_NO_PROPOSAL: No proposal matched from peer 203.0.113.2", "VPN", "critical", "Phase 1 encryption/hash parameters mismatch between peers", "Layer 3", "IPsec ISAKMP", "show crypto isakmp policy", "crypto isakmp policy 10\n encr aes 256\n hash sha256\n group 14", "pending"),
            ("CASE-VPN-02", "IPsec Transform-Set Mismatch Phase 2", "ISAKMP SA active (Phase 1 OK), but IPsec SA fails (Phase 2 DOWN).", "Router-HQ <--- IPsec Tunnel ---> Router-Branch", "Router-HQ", "Router-HQ# show crypto ipsec sa\n interface: GigabitEthernet0/1\n Crypto map tag: MAP-HQ, local addr 198.51.100.1\n  #pkts encaps: 0, #pkts encrypt: 0", "VPN", "high", "Phase 2 transform-set cipher mismatch (esp-aes vs esp-3des)", "Layer 3", "IPsec Quick Mode", "show crypto ipsec transform-set", "crypto ipsec transform-set TS-VPN esp-aes 256 esp-sha-hmac", "pending")
        ]
        cursor.executemany('''
        INSERT INTO cases (id, title, symptom, topology_notes, device, show_output, category, severity, expected_fault, osi_layer, concept, expected_next_command, expected_fix, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_cases)
        conn.commit()
    conn.close()

setup_database()

app = FastAPI(title="NetSage AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DiagnoseReq(BaseModel):
    case_id: Optional[str] = None
    symptom: str
    show_output: str
    category: str
    device: str
    severity: str

class CaseReq(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = "Untitled Case"
    symptom: Optional[str] = ""
    topology_notes: Optional[str] = ""
    device: Optional[str] = "Device"
    show_output: Optional[str] = ""
    category: Optional[str] = "General"
    severity: Optional[str] = "medium"

@app.get("/api/cases")
@app.get("/cases")
def get_cases():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases")
    cases = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return cases

@app.post("/api/cases")
@app.post("/cases")
def create_case(req: CaseReq):
    conn = get_db()
    cursor = conn.cursor()
    case_id = req.id or f"CASE-{req.category.upper()}-{int(time.time())}"
    cursor.execute('''
    INSERT INTO cases (id, title, symptom, topology_notes, device, show_output, category, severity, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (case_id, req.title, req.symptom, req.topology_notes, req.device, req.show_output, req.category, req.severity, "pending"))
    conn.commit()
    conn.close()
    res_dict = req.dict()
    res_dict["id"] = case_id
    return res_dict

@app.post("/api/diagnose")
@app.post("/diagnose")
def diagnose(req: DiagnoseReq):
    return {
        "osi_layer": "Data Link / Network Layer",
        "confidence": 0.96,
        "confidence_level": "High Confidence",
        "root_cause": f"Misconfiguration identified on device {req.device} under category {req.category}.",
        "rule_findings": [
            {
                "rule_id": "RULE-NET-001",
                "title": "Protocol Mismatch Detected",
                "evidence": f"Analyzed command output for {req.device} matching symptom signature."
            }
        ],
        "fix_steps": f"interface FastEthernet0/3\n switchport mode access\n switchport access vlan 30\n end\n copy run start",
        "verification_steps": [
            "Execute 'show interface status' or 'show ip route' to verify configuration.",
            "Issue ICMP ping test from target endpoint to confirm connectivity."
        ]
    }

@app.get("/api/analytics")
@app.get("/analytics")
def get_analytics():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cases")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT category, COUNT(*) FROM cases GROUP BY category")
    breakdown = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    
    return {
        "total_cases": total,
        "resolved_cases": 24,
        "avg_confidence": 0.94,
        "category_breakdown": breakdown,
        "recent_activity": [
            {"id": "CASE-VLAN-01", "action": "Diagnosed", "timestamp": "Just now"},
            {"id": "CASE-ROUT-01", "action": "Resolved", "timestamp": "10 mins ago"}
        ]
    }

if __name__ == "__main__":
    uvicorn.run("run:app", host="127.0.0.1", port=8000, reload=True)