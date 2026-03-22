"""
The main file which will be run on the Raspberry Pi.

It will create the Context object and run the main loop.
"""

from payload.constants import LOGS_PATH
from payload.context import Context
from payload.data_handling.logger import Logger
from payload.hardware.firm import FIRM
from payload.mock.mock_firm import MockFIRM
from payload.utils import arg_parser


def create_firm_from_args(args):
    """Create the correct FIRM implementation based on CLI args."""
    if args.mode == "real":
        return FIRM()

    if args.mode == "mock":
        return MockFIRM(
            real_time_replay=not args.fast_replay,
            log_file_path=args.path,
        )

    if args.mode == "pretend":
        return FIRM(
            is_pretend=True,
            log_file_path=args.path,
        )

    raise ValueError(f"Unknown mode: {args.mode}")


def create_grave_from_args(args):
    if args.mode == "real":
        from payload.hardware.grave import Grave  # noqa: PLC0415
        return Grave()

    if args.mode in {"mock", "pretend"}:
        from payload.mock.mock_grave import MockGrave  # noqa: PLC0415
        return MockGrave()

    raise ValueError(f"Unknown mode: {args.mode}")

def create_zombie_from_args(args):
    if args.mode == "real":
        from payload.hardware.zombie import Zombie  # noqa: PLC0415
        return Zombie()

    if args.mode in {"mock", "pretend"}:
        from payload.mock.mock_zombie import MockZombie  # noqa: PLC0415
        return MockZombie()
    raise ValueError(f"Unknown mode: {args.mode}")


def create_components(args):
    """Creates the system components needed for the payload system."""
    firm = create_firm_from_args(args)
    logger = Logger(LOGS_PATH)
    return firm, logger


def run_payload(*, use_grave: bool, use_zombie: bool):
    args = arg_parser()
    firm, logger = create_components(args)
    grave = create_grave_from_args(args) if use_grave else None
    zombie = create_zombie_from_args(args) if use_zombie else None
    context = Context(
        grave=grave,
        zombie=zombie,
        firm=firm,
        logger=logger,
    )
    run_flight_loop(context)


def run_grave():
    """Runs the code for Grave."""
    run_payload(use_grave=True, use_zombie=False)


def run_zombie():
    """Runs the code for Zombie."""
    run_payload(use_grave=False, use_zombie=True)


def run_flight_loop(context: Context):
    """Runs the main loop for the code."""
    try:
        context.start()
        while True:
            context.update()
    except KeyboardInterrupt:
        pass
    finally:
        context.stop()
