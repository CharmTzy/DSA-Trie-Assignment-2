from server import parse_args, run_server


if __name__ == "__main__":
    args = parse_args()
    run_server(host=args.host, port=args.port)
