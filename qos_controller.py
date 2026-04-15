from pox.core import core
import pox.openflow.libopenflow_01 as of
import time

log = core.getLogger()

class QoSController(object):
    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)

    def _handle_PacketIn(self, event):
        try:
            packet = event.parsed

 
            msg = of.ofp_packet_out()
            msg.data = event.ofp
            msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            self.connection.send(msg)


            ip_packet = packet.find('ipv4')
            if not ip_packet:
                return

            flow_msg = of.ofp_flow_mod()
            flow_msg.match = of.ofp_match.from_packet(packet)

            if ip_packet.protocol == 17:   # UDP
                flow_msg.priority = 100
                log.info("HIGH priority traffic (UDP)")
            else:
                flow_msg.priority = 10
                log.info("LOW priority traffic")
                time.sleep(0.05)  # Delay for low priority

            flow_msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            self.connection.send(flow_msg)

        except Exception:
            # Ignore parsing errors to avoid crash
            return


def launch():
    def start_switch(event):
        log.info("Switch connected")
        QoSController(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)
        log.info("Switch connected")
        QoSController(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)
