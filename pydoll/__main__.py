# pydoll/__main__.py
import sys
import argparse

# Get version dynamically
try:
    from importlib.metadata import version as pkg_version
except ImportError:
    from importlib_metadata import version as pkg_version  # for Python<3.8

def main():
    parser = argparse.ArgumentParser(
        description="Run Pydoll commands. Currently supported: serve."
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"pydoll {pkg_version('pydoll')}",
        help="Show Pydoll version and exit"
    )

    subparsers = parser.add_subparsers(dest="command")

    # Serve subcommand
    serve_parser = subparsers.add_parser("serve", help="Run the Pydoll HTTP server")
    serve_parser.add_argument(
        "-H", "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    serve_parser.add_argument(
        "-p", "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    serve_parser.add_argument(
        "-r", "--reload",
        action="store_true",
        help="Enable autoreload"
    )

    args = parser.parse_args()

    if args.command == "serve":
        import uvicorn
        uvicorn.run(
            "pydoll.serve:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
        )
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
