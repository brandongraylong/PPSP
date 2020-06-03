import sys

from ppsp import ppsp


def main():
    ppsp('ping google.com', '(.*)(icmp_seq=9)(.*)')

if __name__ == "__main__":
    main()
