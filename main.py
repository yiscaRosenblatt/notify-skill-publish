# main_send_weekly.py

import asyncio
import argparse
from tasks.notify_skill_publish import notify_skill_published

parser = argparse.ArgumentParser()
parser.add_argument("--skill_id", type=str, required=True)
args = parser.parse_args()

if __name__ == "__main__":
    asyncio.run(notify_skill_published(args.skill_id))

