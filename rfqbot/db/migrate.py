import argparse
import subprocess
import shlex


def run_alembic(args):
    cmd = ["alembic"] + shlex.split(args)
    subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser(description="Alembic DB Migration Helper")
    parser.add_argument("-m", "--message", help="Create new migration")
    parser.add_argument("-u", "--upgrade", action="store_true", help="Upgrade to head")
    parser.add_argument(
        "-d", "--downgrade", action="store_true", help="Downgrade one revision"
    )
    parser.add_argument("-rev", help="Specify downgrade revision(optional)")
    parser.add_argument(
        "-c", "--current", action="store_true", help="Show current revision"
    )
    parser.add_argument(
        "-H", "--history", action="store_true", help="Show migration history"
    )
    parser.add_argument(
        "-stamp",
        action="store_true",
        help="Mark db as current without running migration",
    )

    args = parser.parse_args()

    if args.message:
        run_alembic(f'revision --autogenerate -m "{args.message}"')
    elif args.upgrade:
        run_alembic("upgrade head")
    elif args.downgrade:
        rev = args.rev if args.rev else "-1"
        run_alembic(f"downgrade {rev}")
    elif args.current:
        run_alembic("current")
    elif args.history:
        run_alembic("history --verbose")
    elif args.stamp:
        run_alembic("stamp head")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
