import datetime
import math
import os
import time

import httpx
from dotenv import load_dotenv
from ibmcloudant.cloudant_v1 import CloudantV1

load_dotenv()

API_BASE = "https://serv.amazingmarvin.com/api"


def date_to_timestamp(date: datetime.datetime) -> int:
    timestamp = time.mktime(date.timetuple()) * 1000
    return int(timestamp)


def today_timestamp() -> int:
    now = datetime.datetime.now()
    return date_to_timestamp(now)


def timestamp_to_date(timestamp: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(timestamp / 1000)


def timestamp_to_datefmt(timestamp: int) -> str:
    fmt_str = "%Y-%m-%d"
    return timestamp_to_date(timestamp).strftime(fmt_str)


async def api_test_endpoint():
    """Test the Amazing Marvin API credentials."""
    endpoint = f"{API_BASE}/test"
    return httpx.post(
        endpoint,
        headers={"X-Full-Access-Token": os.environ.get("FULL_ACCESS_TOKEN")},
    )


class Task:
    """TODO: Convert to a dataclass"""

    def __init__(self, data):
        self.data = data

    @property
    def title(self):
        return self.data["doc"]["title"]

    @property
    def done(self):
        return self.data["doc"].get("done", False)

    @property
    def is_starred(self):
        return self.data["doc"].get("isStarred", 0)

    @property
    def cycle_time(self):
        """Compute the cycle time in days.

        Cycle time is the difference between when a task was created and when it was finished.
        """
        t = self.data
        return (t["doc"]["doneAt"] - t["doc"]["createdAt"]) / (24 * 60 * 60 * 1000)


class AmazingCloudAntClient:
    @property
    def client(self):
        return CloudantV1.new_instance()

    @property
    def db_name(self) -> str:
        try:
            return os.environ["CLOUDANT_SYNC_DB"]
        except KeyError:
            raise Exception("CLOUDANT_SYNC_DB environment variable was not found. You must configure your .env file with this variable")

    def server_information(self):
        return self.client.get_server_information().get_result()

    def get_db_info(self):
        return self.client.get_database_information(db=self.db_name).get_result()

    def _get_all_tasks(self):
        """Retrieve all Task-type documents from the DB.

        See: https://github.com/IBM/cloudant-python-sdk/blob/main/ibmcloudant/cloudant_v1.py#L1163
        """
        type = "Tasks"
        response = self.client.post_all_docs(db=self.db_name, include_docs=True).get_result()
        all_tasks = [r for r in response["rows"] if r["doc"].get("db") is not None and r["doc"].get("db") == type]
        return all_tasks

    def get_all_tasks(self):
        return [Task(t) for t in self._get_all_tasks()]

    def get_task_stats(self, since: int = None):
        all_tasks = self._get_all_tasks()
        result = {"cumulative_flow": {}}

        # Filter tasks by `since` date
        tasks = all_tasks if since is None else [t for t in all_tasks if t["doc"]["createdAt"] >= since]

        # Sort tasks by `createdAt`
        tasks_sorted = sorted(tasks, key=lambda t: t["doc"]["createdAt"])

        # Starting with first task date, iterate by date and find all tasks created
        # (on or) before that day.
        first_task_date = tasks_sorted[0]["doc"]["createdAt"]
        today_date = today_timestamp()
        diff = today_date - first_task_date
        diff_in_days = math.floor(diff / (24 * 60 * 60 * 1000))

        # Iterate over those tasks and filter out completed tasks
        # Count total complete and incomplete tasks as of that day
        for i in range(diff_in_days):
            day_stamp = first_task_date + (i * 24 * 60 * 60 * 1000)
            result["cumulative_flow"][day_stamp] = {
                "cumulative_incomplete": len(
                    [
                        t
                        for t in tasks_sorted
                        if t["doc"]["createdAt"] <= day_stamp
                        and (not t["doc"].get("done") or (t["doc"].get("done") and t["doc"]["doneAt"] > day_stamp))
                    ]
                ),
                "cumulative_complete": len(
                    [
                        t
                        for t in tasks_sorted
                        if t["doc"]["createdAt"] <= day_stamp and t["doc"].get("done") and t["doc"].get("doneAt") <= day_stamp
                    ]
                ),
            }

        result["avg_daily_throughput"] = len([t for t in tasks_sorted if t["doc"].get("done")]) / diff_in_days
        result["avg_daily_backlog"] = len([t for t in tasks_sorted if not t["doc"].get("done")]) / diff_in_days

        return result

    def get_task_stats_for_chart(self, since: int = None):
        # matplotlib expects a list (series) of data for each: x, y1, y2
        result = {
            "dates": [],
            "incomplete": [],
            "complete": [],
        }

        task_stats = self.get_task_stats(since)
        for key, val in task_stats["cumulative_flow"].items():
            result["dates"].append(timestamp_to_date(key))
            result["incomplete"].append(val["cumulative_incomplete"])
            result["complete"].append(val["cumulative_complete"])

        return result

    def get_task_stats_as_csv(self):
        result = []
        task_stats = self.get_task_stats()

        # Headers
        result.append(["Date", "Incomplete", "Complete"])

        # Data
        for key, val in task_stats["cumulative_flow"].items():
            result.append([key, val["cumulative_incomplete"], val["cumulative_complete"]])

        # Print
        for r in result:
            print(",".join([str(r[0]), str(r[1]), str(r[2])]))

    def get_tasks_added_removed_between(self, start=None, end=None):
        """Find the tasks between two given dates to compare created v. completed for the period."""
        result = {}

        if not start:
            start = datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)
        if not end:
            end = start + datetime.timedelta(days=1)

        start_ts = date_to_timestamp(start)
        end_ts = date_to_timestamp(end)

        all_tasks = self._get_all_tasks()

        result["created"] = [t for t in all_tasks if start_ts < t["doc"]["createdAt"] < end_ts]
        result["completed"] = [t for t in all_tasks if start_ts < t["doc"].get("doneAt", 0) < end_ts]

        return result
