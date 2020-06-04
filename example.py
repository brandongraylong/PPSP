import argparse, logging

from ppsp import ppsp


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', 
        '--command', 
        action='store', 
        dest='command', 
        type=str, 
        required=True,
        default=None,
        help='Command to execute via shell.'
    )
    parser.add_argument(
        '-e', 
        '--exit-condition', 
        action='store', 
        dest='exit_condition',
        type=str, 
        required=False, 
        default=None,
        help='Python3 regular expression string.'
    )
    parser.add_argument(
        '-v', 
        '--verbose', 
        action='store_true', 
        dest='verbose',
        required=False,
        default=False,
        help='Verbose flag. If set, PPSP will provide helpful output.'
    )
    args = parser.parse_args()

    ppsp(args.command, args.verbose, args.exit_condition)


if __name__ == "__main__":
    main()
