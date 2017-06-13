from dnstest.dig import DigBuilder

def main():
    print("Running test")
    print("example.com:")
    ret = DigBuilder("example.com", server="100.99.1.2", type="A").run()
    list(map(print, ret))
    print("foo.bar:")
    ret = DigBuilder("foo.bar", server="100.99.1.2", type="A").run()
    list(map(print, ret))

if __name__ == '__main__':
    main()