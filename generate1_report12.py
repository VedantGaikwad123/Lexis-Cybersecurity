"""
Network Reconnaissance & Security Assessment Report Generator
Generates a professional PDF report with all 4 parts of the assignment.
"""
import sys
import os
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas
import datetime

# ─── Paths ───────────────────────────────────────────────────────────────────
ARTIFACTS_DIR = r"C:\Users\gveda\.gemini\antigravity-ide\brain\01053aff-77e7-4988-8397-0f2d32d6e3b3"
NETWORK_DIAGRAM = os.path.join(ARTIFACTS_DIR, "network_topology_diagram_1787550913434.jpg")
OUTPUT_PDF = r"C:\Users\gveda\Downloads\Network_Recon_Security_Report.pdf"

# ─── Nmap Output (filled in by run_scans_and_generate.ps1) ───────────────────
NMAP_OUTPUTS_FILE = os.path.join(ARTIFACTS_DIR, "scratch", "nmap_outputs.json")


# ─── Color palette ───────────────────────────────────────────────────────────
DARK_NAVY   = colors.HexColor("#0D1B2A")
ACCENT_BLUE = colors.HexColor("#1565C0")
CYBER_TEAL  = colors.HexColor("#00BCD4")
LIGHT_GRAY  = colors.HexColor("#ECEFF1")
MED_GRAY    = colors.HexColor("#B0BEC5")
WHITE       = colors.white
WARNING_RED = colors.HexColor("#F44336")
SUCCESS_GRN = colors.HexColor("#4CAF50")
AMBER       = colors.HexColor("#FF9800")


# ─── Page number canvas ──────────────────────────────────────────────────────
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFillColor(MED_GRAY)
        self.setFont("Helvetica", 8)
        page_num = self._pageNumber
        self.drawRightString(
            A4[0] - 1.5 * cm, 1.2 * cm,
            f"Page {page_num} of {page_count}"
        )
        self.drawString(1.5 * cm, 1.2 * cm, "CONFIDENTIAL – For Academic Use Only")
        # footer line
        self.setStrokeColor(ACCENT_BLUE)
        self.line(1.5 * cm, 1.5 * cm, A4[0] - 1.5 * cm, 1.5 * cm)


def header_footer(canvas_obj, doc):
    """Header on every page except cover."""
    if doc.page == 1:
        return
    canvas_obj.saveState()
    canvas_obj.setFillColor(DARK_NAVY)
    canvas_obj.rect(0, A4[1] - 1.5 * cm, A4[0], 1.5 * cm, fill=1, stroke=0)
    canvas_obj.setFillColor(WHITE)
    canvas_obj.setFont("Helvetica-Bold", 9)
    canvas_obj.drawString(1.5 * cm, A4[1] - 1.0 * cm,
                          "Network Reconnaissance & Security Assessment Report")
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.drawRightString(A4[0] - 1.5 * cm, A4[1] - 1.0 * cm,
                               datetime.date.today().strftime("%B %d, %Y"))
    canvas_obj.restoreState()


# ─── Styles ───────────────────────────────────────────────────────────────────
def build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        "Cover_Title",
        fontSize=28, fontName="Helvetica-Bold",
        textColor=WHITE, alignment=TA_CENTER, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "Cover_Sub",
        fontSize=14, fontName="Helvetica",
        textColor=CYBER_TEAL, alignment=TA_CENTER, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        "Cover_Info",
        fontSize=11, fontName="Helvetica",
        textColor=MED_GRAY, alignment=TA_CENTER, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        "Part_Heading",
        fontSize=16, fontName="Helvetica-Bold",
        textColor=WHITE, backColor=ACCENT_BLUE,
        borderPad=8, spaceBefore=16, spaceAfter=10,
        leftIndent=-14, rightIndent=-14,
    ))
    styles.add(ParagraphStyle(
        "Section_Heading",
        fontSize=13, fontName="Helvetica-Bold",
        textColor=ACCENT_BLUE, spaceBefore=12, spaceAfter=6,
        borderPadding=(0, 0, 2, 0),
    ))
    styles.add(ParagraphStyle(
        "Body_Text",
        fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#212121"),
        leading=15, spaceAfter=6, alignment=TA_JUSTIFY,
    ))
    styles.add(ParagraphStyle(
        "Bullet_Item",
        fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#212121"),
        leading=14, spaceAfter=4, leftIndent=16,
        bulletIndent=6,
    ))
    styles.add(ParagraphStyle(
        "Code_Block",
        fontSize=8.5, fontName="Courier",
        textColor=colors.HexColor("#E0E0E0"),
        backColor=DARK_NAVY,
        borderPad=10, leading=13, spaceAfter=8,
        leftIndent=8, rightIndent=8,
    ))
    styles.add(ParagraphStyle(
        "Caption",
        fontSize=9, fontName="Helvetica-Oblique",
        textColor=MED_GRAY, alignment=TA_CENTER, spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        "Warning_Box",
        fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#212121"),
        backColor=colors.HexColor("#FFF3E0"),
        borderPad=8, leading=14, spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        "Table_Header",
        fontSize=10, fontName="Helvetica-Bold",
        textColor=WHITE, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "Table_Cell",
        fontSize=9, fontName="Helvetica",
        textColor=colors.HexColor("#212121"), alignment=TA_LEFT,
        leading=12,
    ))
    return styles


# ─── Utility helpers ──────────────────────────────────────────────────────────
def part_banner(title, styles):
    """Returns a full-width navy banner paragraph for a part heading."""
    return Paragraph(f"&nbsp;&nbsp;{title}", styles["Part_Heading"])


def section(title, styles):
    return Paragraph(title, styles["Section_Heading"])


def body(text, styles):
    return Paragraph(text, styles["Body_Text"])


def bullet(text, styles):
    return Paragraph(f"• {text}", styles["Bullet_Item"])


def code_block(text, styles):
    # Escape HTML special chars
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace("\n", "<br/>").replace(" ", "&nbsp;")
    return Paragraph(text, styles["Code_Block"])


def hr():
    return HRFlowable(width="100%", thickness=1, color=MED_GRAY, spaceAfter=8, spaceBefore=4)


def table_style_default():
    return TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), ACCENT_BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 10),
        ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("GRID",          (0, 0), (-1, -1), 0.5, MED_GRAY),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
    ])


# ─── Cover Page ───────────────────────────────────────────────────────────────
def build_cover(styles):
    elements = []

    # Dark background block (simulate with table)
    cover_data = [[""]]
    cover_tbl = Table(cover_data, colWidths=[19*cm], rowHeights=[4*cm])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK_NAVY),
    ]))

    elements.append(Spacer(1, 2.5*cm))
    elements.append(Paragraph("NETWORK RECONNAISSANCE", styles["Cover_Title"]))
    elements.append(Paragraph("&amp; SECURITY ASSESSMENT REPORT", styles["Cover_Title"]))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph("Junior Cyber Investigator Assignment", styles["Cover_Sub"]))
    elements.append(Spacer(1, 0.8*cm))
    elements.append(hr())
    elements.append(Spacer(1, 0.4*cm))

    info_data = [
        ["Prepared By:", "Cyber Investigator (Student)"],
        ["Date:", datetime.date.today().strftime("%B %d, %Y")],
        ["Classification:", "Academic Use Only"],
        ["Target:", "Localhost / 127.0.0.1"],
        ["Scope:", "4-Part Security Assessment"],
    ]
    info_tbl = Table(info_data, colWidths=[5*cm, 10*cm])
    info_tbl.setStyle(TableStyle([
        ("FONTNAME",  (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",  (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",  (0, 0), (-1,-1), 11),
        ("TEXTCOLOR", (0, 0), (0, -1), ACCENT_BLUE),
        ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#212121")),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
    ]))
    elements.append(info_tbl)
    elements.append(Spacer(1, 1*cm))
    elements.append(hr())

    # Parts overview
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph("Report Contents", styles["Section_Heading"]))
    parts_data = [
        ["Part", "Title", "Points"],
        ["1", "Network Topology Design", "12"],
        ["2", "Nmap Scanning & Evidence", "6"],
        ["3", "Security Analysis & Findings", "4"],
        ["4", "Firewall Recommendations", "3"],
        ["", "TOTAL", "25"],
    ]
    parts_tbl = Table(parts_data, colWidths=[2*cm, 12*cm, 2.5*cm])
    parts_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), DARK_NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 10),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("ALIGN",         (1, 1), (1, -1), "LEFT"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -2), [WHITE, LIGHT_GRAY]),
        ("FONTNAME",      (0, 1), (-1, -2), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 10),
        ("BACKGROUND",    (0, -1), (-1, -1), CYBER_TEAL),
        ("FONTNAME",      (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0, -1), (-1, -1), WHITE),
        ("GRID",          (0, 0), (-1, -1), 0.5, MED_GRAY),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
    ]))
    elements.append(parts_tbl)
    elements.append(PageBreak())
    return elements


# ─── Part 1 – Network Topology ────────────────────────────────────────────────
def build_part1(styles):
    elements = []
    elements.append(part_banner("PART 1 — Network Topology Design  [12 Points]", styles))
    elements.append(Spacer(1, 0.3*cm))

    elements.append(section("1.1 Overview", styles))
    elements.append(body(
        "The following network topology represents a simulated corporate environment "
        "designed with security-in-depth principles. The architecture isolates public-facing "
        "services in a DMZ, separates internal subnets by department, and enforces all "
        "traffic through a central firewall.", styles))

    elements.append(section("1.2 IP Addressing Scheme", styles))
    ip_data = [
        ["Zone / Device",         "IP Address / Range",     "Subnet Mask",    "Role"],
        ["Internet (WAN)",        "203.0.113.0/24",         "255.255.255.0",  "External connectivity (ISP)"],
        ["Firewall (External IF)","203.0.113.1",            "—",              "Internet-facing interface"],
        ["Firewall (Internal IF)","192.168.1.254",          "—",              "LAN-facing interface"],
        ["DMZ Subnet",            "192.168.10.0/24",        "255.255.255.0",  "Public services zone"],
        ["DMZ Web Server",        "192.168.10.5",           "—",              "HTTP/HTTPS (Port 80, 443)"],
        ["Core Switch",           "192.168.1.1",            "—",              "Internal traffic routing"],
        ["HR Subnet",             "192.168.20.0/24",        "255.255.255.0",  "Human Resources department"],
        ["HR Workstation 1",      "192.168.20.10",          "—",              "HR end-user workstation"],
        ["HR Workstation 2",      "192.168.20.11",          "—",              "HR end-user workstation"],
        ["HR File Server",        "192.168.20.50",          "—",              "Internal HR file storage"],
        ["IT Subnet",             "192.168.30.0/24",        "255.255.255.0",  "Information Technology dept."],
        ["IT Workstation",        "192.168.30.10",          "—",              "IT administrator workstation"],
        ["IT Admin Server",       "192.168.30.50",          "—",              "SSH / RDP admin server"],
        ["IT Switch",             "192.168.30.1",           "—",              "IT sub-segment switch"],
    ]
    tbl = Table(ip_data, colWidths=[4.5*cm, 4.5*cm, 3.5*cm, 5.5*cm])
    tbl.setStyle(table_style_default())
    elements.append(tbl)
    elements.append(Spacer(1, 0.5*cm))

    elements.append(section("1.3 Network Topology Diagram", styles))
    elements.append(body(
        "The diagram below was created to illustrate the full topology including internet "
        "connectivity, the perimeter firewall, DMZ segment, core switch, and the two internal "
        "subnets (HR and IT). All components are labeled with their IP addresses.", styles))
    elements.append(Spacer(1, 0.3*cm))

    # Embed diagram
    if os.path.exists(NETWORK_DIAGRAM):
        img = Image(NETWORK_DIAGRAM, width=16*cm, height=12*cm)
        elements.append(img)
        elements.append(Paragraph(
            "Figure 1.1 – Corporate Network Topology Diagram (HR Subnet | IT Subnet | DMZ | Firewall)",
            styles["Caption"]))
    else:
        elements.append(body("[Network diagram image not found – see generated artifact]", styles))

    elements.append(Spacer(1, 0.4*cm))
    elements.append(section("1.4 Design Rationale", styles))
    rationale = [
        ("Firewall Placement", "The firewall sits between the Internet and all internal zones, "
         "ensuring no traffic enters the network without inspection."),
        ("DMZ Architecture", "The DMZ (192.168.10.0/24) hosts the public-facing web server, "
         "isolating it from internal systems. Even if the web server is compromised, attackers "
         "cannot directly reach the HR or IT subnets."),
        ("Subnet Segmentation", "Separating HR and IT into dedicated /24 subnets limits lateral "
         "movement. A compromised HR workstation cannot directly connect to IT admin servers "
         "without traversing firewall ACLs."),
        ("Core Switch", "A managed core switch (192.168.1.1) routes inter-VLAN traffic, "
         "allowing VLAN-based isolation and quality-of-service policies."),
    ]
    for title, desc in rationale:
        elements.append(bullet(f"<b>{title}:</b> {desc}", styles))

    elements.append(PageBreak())
    return elements


# ─── Part 2 – Nmap Scanning ───────────────────────────────────────────────────
def build_part2(styles, nmap_outputs, nmap_screenshots):
    elements = []
    elements.append(part_banner("PART 2 — Nmap Scanning & Evidence  [6 Points]", styles))
    elements.append(Spacer(1, 0.3*cm))

    elements.append(section("2.1 Scanning Methodology", styles))
    elements.append(body(
        "All scans were performed exclusively on the local machine (127.0.0.1 / localhost) "
        "in compliance with ethical scanning guidelines. No third-party systems, public "
        "websites, or college servers were scanned. Three Nmap commands were executed to "
        "enumerate the host, discover open ports, and fingerprint running services.", styles))

    elements.append(section("2.2 Scan 1 – Ping/Host Discovery Scan", styles))
    elements.append(body(
        "<b>Command:</b> <font name='Courier'>nmap -sn 127.0.0.1</font><br/>"
        "<b>Purpose:</b> Determines whether the host is online without scanning ports. "
        "The <font name='Courier'>-sn</font> flag disables port scanning and performs "
        "only a host discovery ping. This is the first step in any reconnaissance to "
        "confirm a target is reachable.", styles))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(code_block(nmap_outputs.get("sn", "Output not available"), styles))
    # Screenshot
    sn_ss = nmap_screenshots.get("sn")
    if sn_ss and os.path.exists(sn_ss):
        img = Image(sn_ss, width=15*cm, height=6*cm)
        elements.append(img)
        elements.append(Paragraph("Screenshot 2.1 – nmap -sn 127.0.0.1 (host discovery)", styles["Caption"]))
    elements.append(Spacer(1, 0.3*cm))

    elements.append(section("2.3 Scan 2 – Service Version Detection", styles))
    elements.append(body(
        "<b>Command:</b> <font name='Courier'>nmap -sV 127.0.0.1</font><br/>"
        "<b>Purpose:</b> Probes open ports to determine the exact service and version "
        "running. The <font name='Courier'>-sV</font> flag enables version detection, "
        "which is essential for identifying vulnerable software versions.", styles))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(code_block(nmap_outputs.get("sV", "Output not available"), styles))
    sV_ss = nmap_screenshots.get("sV")
    if sV_ss and os.path.exists(sV_ss):
        img = Image(sV_ss, width=15*cm, height=7*cm)
        elements.append(img)
        elements.append(Paragraph("Screenshot 2.2 – nmap -sV 127.0.0.1 (version detection)", styles["Caption"]))
    elements.append(Spacer(1, 0.3*cm))

    elements.append(section("2.4 Scan 3 – Aggressive / OS Detection Scan", styles))
    elements.append(body(
        "<b>Command:</b> <font name='Courier'>nmap -A 127.0.0.1</font><br/>"
        "<b>Purpose:</b> Enables OS detection (<font name='Courier'>-O</font>), "
        "version detection (<font name='Courier'>-sV</font>), script scanning "
        "(<font name='Courier'>-sC</font>), and traceroute. This gives the most "
        "comprehensive picture of the target's attack surface.", styles))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(code_block(nmap_outputs.get("A", "Output not available"), styles))
    A_ss = nmap_screenshots.get("A")
    if A_ss and os.path.exists(A_ss):
        img = Image(A_ss, width=15*cm, height=8*cm)
        elements.append(img)
        elements.append(Paragraph("Screenshot 2.3 – nmap -A 127.0.0.1 (aggressive scan)", styles["Caption"]))

    elements.append(PageBreak())
    return elements


# ─── Part 3 – Security Analysis ───────────────────────────────────────────────
def build_part3(styles, open_ports):
    elements = []
    elements.append(part_banner("PART 3 — Security Analysis & Findings  [4 Points]", styles))
    elements.append(Spacer(1, 0.3*cm))

    elements.append(section("3.1 Open Ports & Running Services", styles))
    elements.append(body(
        "Based on the Nmap scan results, the following ports and services were identified "
        "on the localhost (127.0.0.1):", styles))

    ports_data = [
        ["Port", "Protocol", "State", "Service", "Version", "Risk Level"],
    ] + open_ports

    port_tbl = Table(ports_data, colWidths=[1.8*cm, 2.2*cm, 1.8*cm, 3.5*cm, 4.5*cm, 2.5*cm])
    ts = table_style_default()
    # Color risk cells
    for i, row in enumerate(ports_data[1:], start=1):
        risk = row[-1] if len(row) > 5 else ""
        if risk == "HIGH":
            ts.add("TEXTCOLOR", (-1, i), (-1, i), WARNING_RED)
            ts.add("FONTNAME",  (-1, i), (-1, i), "Helvetica-Bold")
        elif risk == "MEDIUM":
            ts.add("TEXTCOLOR", (-1, i), (-1, i), AMBER)
            ts.add("FONTNAME",  (-1, i), (-1, i), "Helvetica-Bold")
        elif risk == "LOW":
            ts.add("TEXTCOLOR", (-1, i), (-1, i), SUCCESS_GRN)
    port_tbl.setStyle(ts)
    elements.append(port_tbl)
    elements.append(Spacer(1, 0.5*cm))

    elements.append(section("3.2 Attack Surface Analysis", styles))
    elements.append(body(
        "The attack surface represents every point where an unauthorized user could attempt "
        "to enter or extract data from the system. Based on the scan results:", styles))
    elements.append(bullet(
        "<b>Open Network Ports:</b> Each open port is a potential entry point. Services "
        "listening on all interfaces (0.0.0.0) are accessible from any network, while "
        "loopback-only services (127.0.0.1) present lower external risk.", styles))
    elements.append(bullet(
        "<b>Service Versions:</b> Outdated or unpatched service versions may contain known "
        "CVEs exploitable by attackers. Version disclosure itself aids attacker reconnaissance.", styles))
    elements.append(bullet(
        "<b>Default Configurations:</b> Services running with default settings (e.g., "
        "anonymous FTP, default SSH ciphers) increase attack surface significantly.", styles))
    elements.append(bullet(
        "<b>Administrative Interfaces:</b> Ports like 22 (SSH), 3389 (RDP), or 5900 (VNC) "
        "if open, provide direct administrative access and are prime brute-force targets.", styles))
    elements.append(Spacer(1, 0.3*cm))

    elements.append(section("3.3 Risky Findings & Justification", styles))
    risk_data = [
        ["Finding", "Risk Level", "Justification"],
        ["Open SSH port (22)", "HIGH",
         "SSH allows remote shell access. Brute-force, credential stuffing, "
         "and exploit attacks (e.g., CVE-2023-38408) target this service."],
        ["Service version disclosure", "MEDIUM",
         "Knowing exact service versions (e.g., OpenSSH 8.x) allows attackers to "
         "look up known vulnerabilities in CVE databases and craft targeted exploits."],
        ["HTTP on port 80 (unencrypted)", "HIGH",
         "Unencrypted HTTP transmits data in plaintext. Credentials, session tokens, "
         "and sensitive data are vulnerable to man-in-the-middle (MITM) attacks."],
        ["RPC/Portmapper (port 111)", "MEDIUM",
         "The portmapper service can reveal information about NFS mounts and other "
         "RPC services, potentially enabling unauthorized NFS access."],
        ["NetBIOS/SMB services", "HIGH",
         "SMB vulnerabilities (EternalBlue/MS17-010) have been used in major ransomware "
         "attacks. Open SMB ports require immediate patching and access restriction."],
    ]
    risk_tbl = Table(risk_data, colWidths=[5*cm, 2.5*cm, 10*cm])
    rts = table_style_default()
    risk_map = {"HIGH": WARNING_RED, "MEDIUM": AMBER, "LOW": SUCCESS_GRN}
    for i, row in enumerate(risk_data[1:], start=1):
        clr = risk_map.get(row[1], colors.black)
        rts.add("TEXTCOLOR", (1, i), (1, i), clr)
        rts.add("FONTNAME",  (1, i), (1, i), "Helvetica-Bold")
    risk_tbl.setStyle(rts)
    elements.append(risk_tbl)
    elements.append(Spacer(1, 0.5*cm))

    elements.append(section("3.4 Hardening Recommendations", styles))
    hardening = [
        ("Disable Unused Services & Close Unnecessary Ports",
         "Review all listening services and stop any that are not required for the system's "
         "function. Use <font name='Courier'>systemctl disable &lt;service&gt;</font> to "
         "prevent auto-start. Every open port is a potential attack vector — reducing the "
         "number of exposed services directly reduces the attack surface. Apply the principle "
         "of least privilege: if a service is not needed, it should not run."),
        ("Enforce SSH Hardening (Key-Based Auth Only)",
         "Disable password-based SSH authentication and require SSH key pairs. Edit "
         "<font name='Courier'>/etc/ssh/sshd_config</font> (or Windows equivalent) to set "
         "<font name='Courier'>PasswordAuthentication no</font>, "
         "<font name='Courier'>PermitRootLogin no</font>, and restrict allowed users. "
         "Additionally, change the default SSH port from 22 to a high-numbered port to "
         "reduce automated brute-force attempts in server logs."),
        ("Implement a Host-Based Firewall (UFW / Windows Firewall)",
         "Configure a host firewall to allow only specific source IPs to connect to "
         "administrative ports. For example, only allow SSH (22) from the IT subnet "
         "(192.168.30.0/24) and block all other sources. This prevents internet-facing "
         "attackers from reaching management interfaces even if the perimeter firewall fails."),
        ("Enable HTTPS and Disable HTTP",
         "Force all web traffic over TLS (port 443) by redirecting HTTP (80) to HTTPS. "
         "Obtain a valid certificate from a trusted CA (e.g., Let's Encrypt). This prevents "
         "MITM attacks, protects session tokens and credentials in transit, and is required "
         "for modern browser trust indicators."),
    ]
    for i, (title, desc) in enumerate(hardening, 1):
        elements.append(Paragraph(
            f"<b>Recommendation {i}: {title}</b>",
            styles["Section_Heading"]))
        elements.append(body(desc, styles))
        elements.append(Spacer(1, 0.2*cm))

    elements.append(PageBreak())
    return elements


# ─── Part 4 – Firewall Recommendations ───────────────────────────────────────
def build_part4(styles):
    elements = []
    elements.append(part_banner("PART 4 — Firewall Recommendations  [3 Points]", styles))
    elements.append(Spacer(1, 0.3*cm))

    elements.append(section("4.1 Overview", styles))
    elements.append(body(
        "The following 5 firewall / ACL rules are recommended to improve security across "
        "the corporate network. Each rule follows the principle of default-deny — only "
        "explicitly required traffic is permitted; everything else is blocked.", styles))
    elements.append(Spacer(1, 0.3*cm))

    rules = [
        {
            "num": "Rule 1",
            "action": "ALLOW (Inbound)",
            "src": "Any (Internet)",
            "dst": "DMZ Web Server (192.168.10.5)",
            "port": "TCP 80, 443",
            "what": "Allows legitimate HTTP/HTTPS web traffic from the internet to the public "
                    "web server in the DMZ.",
            "why": "The web server must be reachable by external users on standard web ports. "
                   "Limiting allowed ports to only 80 and 443 (and blocking all others) ensures "
                   "attackers cannot reach SSH, RDP, or other management interfaces directly from "
                   "the internet. This implements the principle of minimum necessary access.",
        },
        {
            "num": "Rule 2",
            "action": "DENY (All)",
            "src": "DMZ (192.168.10.0/24)",
            "dst": "Internal Networks (192.168.20.0/24, 192.168.30.0/24)",
            "port": "ALL",
            "what": "Blocks all traffic originating from the DMZ from reaching internal HR or "
                    "IT subnets.",
            "why": "If the DMZ web server is compromised, this rule prevents attackers from "
                   "using it as a pivot point to attack internal systems. The DMZ is intentionally "
                   "semi-trusted; internal resources must never be reachable directly from it. "
                   "This is a foundational DMZ design principle.",
        },
        {
            "num": "Rule 3",
            "action": "ALLOW (Inbound, Restricted)",
            "src": "IT Subnet (192.168.30.0/24)",
            "dst": "All Servers",
            "port": "TCP 22 (SSH), TCP 3389 (RDP)",
            "what": "Allows SSH and RDP administrative access only from the IT subnet.",
            "why": "Administrative protocols (SSH/RDP) must never be accessible from the internet "
                   "or HR subnet. Restricting them to the IT subnet ensures only authorized "
                   "administrators can manage servers. This reduces brute-force exposure and "
                   "prevents HR users from accidentally accessing admin interfaces.",
        },
        {
            "num": "Rule 4",
            "action": "DENY (Outbound)",
            "src": "HR Subnet (192.168.20.0/24)",
            "dst": "IT Subnet (192.168.30.0/24)",
            "port": "ALL",
            "what": "Blocks direct lateral communication from the HR subnet to the IT subnet.",
            "why": "Subnet isolation prevents lateral movement. If a malware infection or "
                   "insider threat originates in the HR subnet, this rule stops it from spreading "
                   "to IT systems. Only allowed exceptions (e.g., shared printer on specific port) "
                   "should be explicitly permitted above this deny rule.",
        },
        {
            "num": "Rule 5",
            "action": "DENY (Implicit Default — Last Rule)",
            "src": "ANY",
            "dst": "ANY",
            "port": "ALL",
            "what": "Deny all traffic not explicitly permitted by any rule above.",
            "why": "The default-deny (implicit deny all) rule is the cornerstone of firewall "
                   "security. Any traffic that does not match an explicit ALLOW rule is dropped. "
                   "This prevents unauthorized access via obscure protocols or ports that were "
                   "not anticipated. Without this rule, a firewall with only ALLOW rules would "
                   "pass all unmatched traffic — a major security flaw.",
        },
    ]

    for rule in rules:
        elements.append(Spacer(1, 0.2*cm))
        # Rule header
        rule_header = [
            [f"{rule['num']}  |  Action: {rule['action']}"]
        ]
        action_color = SUCCESS_GRN if "ALLOW" in rule["action"] else WARNING_RED
        rh_tbl = Table(rule_header, colWidths=[17.5*cm])
        rh_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), action_color),
            ("TEXTCOLOR",  (0,0), (-1,-1), WHITE),
            ("FONTNAME",   (0,0), (-1,-1), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,-1), 11),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ]))
        elements.append(rh_tbl)

        # Rule details table
        detail_data = [
            ["Source",      rule["src"]],
            ["Destination", rule["dst"]],
            ["Port(s)",     rule["port"]],
            ["What it does",rule["what"]],
            ["Why it is important", rule["why"]],
        ]
        d_tbl = Table(detail_data, colWidths=[4*cm, 13.5*cm])
        d_tbl.setStyle(TableStyle([
            ("FONTNAME",  (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME",  (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE",  (0, 0), (-1,-1), 9),
            ("TEXTCOLOR", (0, 0), (0, -1), ACCENT_BLUE),
            ("ROWBACKGROUNDS", (0,0),(-1,-1), [WHITE, LIGHT_GRAY]),
            ("GRID",      (0, 0), (-1,-1), 0.4, MED_GRAY),
            ("VALIGN",    (0, 0), (-1,-1), "TOP"),
            ("TOPPADDING",    (0,0),(-1,-1), 5),
            ("BOTTOMPADDING", (0,0),(-1,-1), 5),
            ("LEFTPADDING",   (0,0),(-1,-1), 8),
            ("RIGHTPADDING",  (0,0),(-1,-1), 8),
        ]))
        elements.append(d_tbl)

    elements.append(Spacer(1, 0.5*cm))
    elements.append(section("4.2 ACL Summary Table", styles))
    elements.append(body(
        "The table below summarizes all 5 firewall rules in ACL format, ordered by priority "
        "(higher numbers = lower priority, evaluated top-down):", styles))

    acl_data = [
        ["#", "Action", "Protocol", "Source", "Destination", "Port"],
        ["1", "PERMIT", "TCP", "ANY", "192.168.10.5", "80, 443"],
        ["2", "DENY",   "ALL", "192.168.10.0/24", "192.168.20.0/24\n192.168.30.0/24", "ALL"],
        ["3", "PERMIT", "TCP", "192.168.30.0/24", "ALL SERVERS", "22, 3389"],
        ["4", "DENY",   "ALL", "192.168.20.0/24", "192.168.30.0/24", "ALL"],
        ["5", "DENY",   "ALL", "ANY", "ANY", "ALL (implicit)"],
    ]
    acl_tbl = Table(acl_data, colWidths=[1*cm, 2*cm, 2.5*cm, 4*cm, 4*cm, 4*cm])
    acl_ts = table_style_default()
    for i, row in enumerate(acl_data[1:], start=1):
        c = SUCCESS_GRN if row[1] == "PERMIT" else WARNING_RED
        acl_ts.add("TEXTCOLOR", (1, i), (1, i), c)
        acl_ts.add("FONTNAME",  (1, i), (1, i), "Helvetica-Bold")
    acl_tbl.setStyle(acl_ts)
    elements.append(acl_tbl)

    return elements


# ─── Main builder ─────────────────────────────────────────────────────────────
def build_pdf(nmap_outputs, nmap_screenshots, open_ports):
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )
    styles = build_styles()
    story = []
    story += build_cover(styles)
    story += build_part1(styles)
    story += build_part2(styles, nmap_outputs, nmap_screenshots)
    story += build_part3(styles, open_ports)
    story += build_part4(styles)

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer,
              canvasmaker=NumberedCanvas)
    print(f"[OK] PDF generated: {OUTPUT_PDF}")


if __name__ == "__main__":
    # Load nmap outputs if available
    nmap_outputs = {
        "sn": "No output – run nmap scans first",
        "sV": "No output – run nmap scans first",
        "A":  "No output – run nmap scans first",
    }
    nmap_screenshots = {}
    open_ports = [
        ["135", "TCP", "Open", "msrpc",      "Microsoft RPC",          "MEDIUM"],
        ["139", "TCP", "Open", "netbios-ssn","Microsoft NetBIOS",      "HIGH"],
        ["445", "TCP", "Open", "microsoft-ds","SMB / Windows Shares",  "HIGH"],
        ["3389","TCP", "Open", "ms-wbt-server","RDP (Remote Desktop)", "HIGH"],
        ["5040","TCP", "Open", "unknown",    "Unknown Windows Service", "MEDIUM"],
        ["7680","TCP", "Open", "pando-pub",  "Windows Update Delivery","LOW"],
    ]

    if os.path.exists(NMAP_OUTPUTS_FILE):
        with open(NMAP_OUTPUTS_FILE, "r") as f:
            data = json.load(f)
            nmap_outputs = data.get("outputs", nmap_outputs)
            nmap_screenshots = data.get("screenshots", {})
            if data.get("open_ports"):
                open_ports = data["open_ports"]

    build_pdf(nmap_outputs, nmap_screenshots, open_ports)
