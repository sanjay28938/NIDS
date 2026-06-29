from scapy.all import sniff

def process_packet(packet):

    print("Packet captured:", packet.summary())

print("Capturing network packets...")

sniff(prn=process_packet, count=20)