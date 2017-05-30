from server import DNSServer,DNSServerType
from netns import NetworkInterface
from dir import Dir
from error import ConfigError

if __name__ == '__main__':
    try:
        Dir.init()
        ni = NetworkInterface("root", 1)
        test = DNSServer(DNSServerType.AUTHORITATIVE, ni)
        test.serve_zone(".")
        test.run()
    except ConfigError as err:
        print("error: {0}".format(err))

