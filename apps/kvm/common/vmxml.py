from . import utils


class VmXmlParse:
    def __init__(self, xml):
        self.xml = xml

    def get_net_devices(self):
        def networks(ctx):
            result = {}
            for net in ctx.xpath('/domain/devices/interface'):
                result['net_type'] = net.xpath('@type')[0]
                result['mac_address'] = net.xpath('mac/@address')[0]
                result['net_name'] = net.xpath('source/@network|source/@bridge|source/@dev')[0]
                target_inst = '' if not net.xpath('target/@dev') else net.xpath('target/@dev')[0]
                link_state = 'up' if not net.xpath('link') else net.xpath('link/@state')[0]
                filterref_inst = '' if not net.xpath('filterref/@filter') else net.xpath('filterref/@filter')[0]
                model_type = net.xpath('model/@type')[0]

            return result

        return utils.get_xml_path(self.xml, func=networks)

    def get_console_port(self):
        console_type = self.get_console_type()
        port = utils.get_xml_path(self.xml, "/domain/devices/graphics[@type='%s']/@port" % console_type)
        return port

    def get_console_type(self):
        console_type = utils.get_xml_path(self.xml, "/domain/devices/graphics/@type")
        return console_type
