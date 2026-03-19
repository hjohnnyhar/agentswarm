from src.cli import parse_args, run_workflow


def main():
    args = parse_args()
    run_workflow(args.topic)


if __name__ == "__main__":
    main()
