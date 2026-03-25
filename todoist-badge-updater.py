#!/usr/bin/env python3
"""
Todoist Badge Updater - Updates the count badge on todoist.desktop via D-Bus
This script fetches tasks from Todoist API and displays the count of tasks
scheduled for today or overdue.
"""

import argparse
import logging
import os
import sys
import time
from typing import Optional

import dbus
import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)
logger.setLevel(log_level)


class TodoistBadgeUpdater:
    """Updates Todoist count badge via D-Bus using Todoist API."""

    TODOIST_API_URL = "https://api.todoist.com/api/v1"

    def __init__(
        self,
        api_token: str,
        app_id: str = "application://todoist.desktop",
        interval: int = 300,
    ):
        """
        Initialize the updater with a Todoist API token.

        Args:
            api_token: Your Todoist API token
            app_id: D-Bus application ID for the launcher entry (defaults to application://todoist.desktop)
            interval: Time interval in seconds between updates (default 300)
        """
        self.api_token = api_token
        self.app_id = app_id
        self.interval = interval
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
        )

    def get_active_tasks(self):
        """
        Fetch all active tasks from Todoist.

        Returns:
            List of task dictionaries from the API

        Raises:
            requests.RequestException: If API call fails
        """
        try:
            response = self.session.get(
                f"{self.TODOIST_API_URL}/tasks/filter",
                params={"query": "today | overdue"},
            )
            response.raise_for_status()
            logger.debug(f"API response: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch tasks from Todoist API: {e}")
            raise

    def count_today_tasks(self) -> int:
        """
        Count tasks scheduled for today or overdue.

        Returns:
            Number of tasks due today or overdue
        """
        try:
            tasks = self.get_active_tasks()
            return len(tasks["results"])
        except Exception as e:
            logger.error(f"Error counting tasks: {e}")
            return 0

    def update_badge_dbus(self, count: int) -> bool:
        """
        Update the count badge on todoist.desktop via D-Bus using Unity LauncherEntry.

        Args:
            count: The count to display on the badge

        Returns:
            True if successful, False otherwise
        """
        try:
            bus = dbus.SessionBus()

            properties = {
                "count-visible": dbus.Boolean(count > 0),
                "count": dbus.UInt32(count),
            }

            msg = dbus.lowlevel.SignalMessage(  # pyright: ignore[reportAttributeAccessIssue]
                "/", "com.canonical.Unity.LauncherEntry", "Update"
            )
            msg.append(self.app_id, signature="s")
            msg.append(properties, signature="a{sv}")
            msg.set_no_reply(True)

            bus.send_message(msg)

            logger.info(
                f"Badge updated to {count} via com.canonical.Unity.LauncherEntry"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to update badge via D-Bus: {e}")
            logger.debug(f"Exception details: {type(e).__name__}: {e}")
            return False

    def run(self) -> Optional[int]:
        """
        Perform the complete update: fetch tasks and update badge periodically.

        Returns:
            The count of tasks, or None if update failed
        """
        try:
            while True:
                count = self.count_today_tasks()
                self.update_badge_dbus(count)
                logger.debug(f"Next update in {self.interval} seconds")
                time.sleep(self.interval)
        except KeyboardInterrupt:
            logger.info("Shutting down...")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Update Todoist count badge via D-Bus")
    parser.add_argument(
        "--token",
        required=False,
        help="Todoist API token (defaults to TODOIST_API_TOKEN env var)",
    )
    parser.add_argument(
        "--desktop-id",
        required=False,
        help="Desktop id of the application\n (defaults to TODOIST_DESKTOP_ID env var, then use application://todoist.desktop as fallback)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Interval in seconds between badge updates (daemon mode)",
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    api_token = args.token
    if not api_token:
        api_token = os.getenv("TODOIST_API_TOKEN")

    if not api_token:
        logger.error(
            "Todoist API token required. "
            "Provide via --token or TODOIST_API_TOKEN environment variable"
        )
        sys.exit(1)

    app_id = args.desktop_id
    if not app_id:
        app_id = os.getenv("TODOIST_DESKTOP_ID", "application://todoist.desktop")
    logger.debug(f"Using application ID: {app_id}")

    updater = TodoistBadgeUpdater(api_token, app_id, args.interval)
    updater.run()

    sys.exit(0)


if __name__ == "__main__":
    main()
