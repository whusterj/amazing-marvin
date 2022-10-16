import datetime
import math
import os
import time

import httpx
from dotenv import load_dotenv
from ibmcloudant.cloudant_v1 import CloudantV1

load_dotenv()

API_BASE = "https://serv.amazingmarvin.com/api"


def today_timestamp() -> int:
    now = datetime.datetime.now()
    timestamp = time.mktime(now.timetuple()) * 1000
    return int(timestamp)


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

    def get_all_tasks(self):
        """Retrieve all Task-type documents from the DB.

        See: https://github.com/IBM/cloudant-python-sdk/blob/main/ibmcloudant/cloudant_v1.py#L1163
        """
        type = "Tasks"
        response = self.client.post_all_docs(db=self.db_name, include_docs=True).get_result()
        all_tasks = [r for r in response["rows"] if r["doc"]["db"] == type]
        return all_tasks

    def get_task_stats(self):
        all_tasks = self.get_all_tasks()
        result = {"cumulative_flow": {}}

        # Sort tasks by `createdAt`
        all_tasks_sorted = sorted(all_tasks, key=lambda t: t["doc"]["createdAt"])

        # Starting with first task date, iterate by date and find all tasks created
        # (on or) before that day.
        first_task_date = all_tasks_sorted[0]["doc"]["createdAt"]
        today_date = today_timestamp()
        diff = today_date - first_task_date
        diff_in_days = math.floor(diff / (24 * 60 * 60 * 1000))

        # Iterate over those tasks and filter out completed tasks
        # Count cumulative incomplete and complete on that day
        for i in range(diff_in_days):
            day_stamp = first_task_date + (i * 24 * 60 * 60 * 1000)
            result["cumulative_flow"][day_stamp] = {
                "cumulative_incomplete": len(
                    [t for t in all_tasks_sorted if t["doc"]["createdAt"] <= day_stamp and not t["doc"].get("done")]
                ),
                "cumulative_complete": len(
                    [
                        t
                        for t in all_tasks_sorted
                        if t["doc"]["createdAt"] <= day_stamp and t["doc"].get("done") and t["doc"].get("doneAt") <= day_stamp
                    ]
                ),
            }

        result["avg_daily_throughput"] = len([t for t in all_tasks_sorted if t["doc"].get("done")]) / diff_in_days
        result["avg_daily_backlog"] = len([t for t in all_tasks_sorted if not t["doc"].get("done")]) / diff_in_days

        return result

    def get_task_stats_for_chart(self):
        # matplotlib expects a list (series) of data for each: x, y1, y2
        result = {
            "dates": [],
            "incomplete": [],
            "complete": [],
        }

        task_stats = self.get_task_stats()
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
