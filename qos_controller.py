from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import ipv4
import time

log = core.getLogger()

class QoSController(object):
    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)

    def _handle_PacketIn(self, event):
        packet = event.parsed
        ip_packet = packet.find('ipv4')

        if not ip_packet:
            return

        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)

        # 🔥 QoS Logic
        if ip_packet.protocol == 17:   # UDP
            msg.priority = 100
            log.info("HIGH priority traffic (UDP)")
        else:
            msg.priority = 10
            log.info("LOW priority traffic")
            time.sleep(0.05)   # add delay for low priority

        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        self.connection.send(msg)


def launch():
    def start_switch(event):
        log.info("Switch connected")
        QoSController(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)