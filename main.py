# TODO: visualise the org structure
# TODO: get people's pictures - download the "ProfileImageAddress"
# TODO: look up their names in the phone book and get their phone extensions and floor

import requests
import time
import logging
import os
from dotenv import load_dotenv
import json

# Load the .env file
load_dotenv()

# Access environment variables
BIG_BOSS_ID = os.getenv("BIG_BOSS_ID")
COOKIE_HEADER = os.getenv("COOKIE_HEADER")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE_NAME = "org_structure.log"
OUTPUT_FILE_NAME = "org_structure.json"

WAIT_TIME = 1  # Wait time between requests cuz I don't wanna get blocked

print(f"BIG_BOSS_ID: {BIG_BOSS_ID}")
print(f"COOKIE_HEADER: {COOKIE_HEADER}")
print(f"BASE_DIR: {BASE_DIR}")


class TreeNode:
    def __init__(self, person_id, full_name, email, job_title):
        self.person_id = person_id
        self.full_name = full_name
        self.email = email
        self.job_title = job_title
        self.children = []


def send_request_directs(person_id, cookie_header) -> requests.Response:
    logging.info(f"Sending request to see who reports to person_id: {person_id}")
    time.sleep(WAIT_TIME)
    response = requests.get(
        f"https://nam.delve.office.com/mt/v3/people/{person_id}/core/directs",
        headers={
            "Accept-Language": "en-US,en;q=0.9,ms;q=0.8",
            "Connection": "keep-alive",
            "Cookie": cookie_header,
            "Referer": f"https://nam.delve.office.com/?u={person_id}&v=work",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Delve-ClientCorrelationId": "b53ca2ad-71f2-49a8-be67-a6c6e00e6432",
            "X-Delve-ClientPlatform": "DelveWeb",
            "X-Delve-Digest": "CfDJ8PNTzaUlhPZBhIanJP3yKPnODo46HD6-wBVqPlvdNHhHPMln0HiHWfAzpHjTee77uwQnVV0UZV1Ca4qmUtbbGzEe8qB9OG6oqGBbu706fmlFYvxeHvpeGinH2H__0Qqozzp1x8R6f84jMRsVXvVa7nK8M9KNO4N0EMOXUi5-7HUGtCPxasJTQgKbZGIhlViznQ",
            "X-Delve-FlightOverrides": "flights='DelveOnOLS,PulseWebFallbackCards,PulseWebContentTypesWave1,PulseWebContentTypeFilter'",
            "X-Delve-ServerCorrelationId": "30dfbba6-9362-2ca7-34aa-03f3257a86f6",
            "X-Edge-Shopping-Flag": "1",
            "accept": "application/json;odata=verbose",
        },
    )
    if response.status_code != 200:
        logging.warning(
            f"Failed to fetch data for person_id: {person_id}, status code: {response.status_code}"
        )
    return response.json()


def send_request_managers(person_id, cookie_header) -> requests.Response:
    logging.info(f"Sending request to see who is the boss of person_id: {person_id}")
    time.sleep(WAIT_TIME)
    response = requests.get(
        f"https://nam.delve.office.com/mt/v3/people/{person_id}/core/managers",
        headers={
            "Accept-Language": "en-US,en;q=0.9,ms;q=0.8",
            "Connection": "keep-alive",
            "Cookie": cookie_header,
            "Referer": f"https://nam.delve.office.com/?u={person_id}&v=work",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Delve-ClientCorrelationId": "b53ca2ad-71f2-49a8-be67-a6c6e00e6432",
            "X-Delve-ClientPlatform": "DelveWeb",
            "X-Delve-Digest": "CfDJ8PNTzaUlhPZBhIanJP3yKPnODo46HD6-wBVqPlvdNHhHPMln0HiHWfAzpHjTee77uwQnVV0UZV1Ca4qmUtbbGzEe8qB9OG6oqGBbu706fmlFYvxeHvpeGinH2H__0Qqozzp1x8R6f84jMRsVXvVa7nK8M9KNO4N0EMOXUi5-7HUGtCPxasJTQgKbZGIhlViznQ",
            "X-Delve-FlightOverrides": "flights='DelveOnOLS,PulseWebFallbackCards,PulseWebContentTypesWave1,PulseWebContentTypeFilter'",
            "X-Delve-ServerCorrelationId": "30dfbba6-9362-2ca7-34aa-03f3257a86f6",
            "X-Edge-Shopping-Flag": "1",
            "accept": "application/json;odata=verbose",
        },
    )
    if response.status_code != 200:
        logging.warning(
            f"Failed to fetch data for person_id: {person_id}, status code: {response.status_code}"
        )
    return response.json()


def build_org_tree(person_id, cookie_header):
    data = send_request_directs(person_id, cookie_header)

    first_smallboss_id = data["d"][0]["AadObjectId"]

    big_boss = send_request_managers(first_smallboss_id, cookie_header)["d"][0]

    root = TreeNode(
        big_boss["AadObjectId"],
        big_boss["FullName"],
        big_boss["Email"],
        big_boss["JobTitle"],
    )

    logging.info(f"ADDED DA TOP G OF DA WHOLE ORG!!!: {root.full_name}")
    stack = [(root, data["d"])]

    while stack:
        node, people = stack.pop()
        for person in people:
            if not person.get("JobTitle"):
                logging.info(f"Skipping person without JobTitle: {person['FullName']}")
                continue
            child_node = TreeNode(
                person["AadObjectId"],
                person["FullName"],
                person["Email"],
                person["JobTitle"],
            )
            node.children.append(child_node)
            logging.info(f"Added person: {child_node.full_name} under {node.full_name}")
            child_data = send_request_directs(person["AadObjectId"], cookie_header)
            if "d" in child_data and child_data["d"]:
                stack.append((child_node, child_data["d"]))

    return root


def print_tree(node, level=0):
    print(" " * level * 2 + node.full_name)
    for child in node.children:
        print_tree(child, level + 1)


# Helper to convert TreeNode to dictionary
def tree_to_dict(node):
    return {
        "person_id": node.person_id,
        "full_name": node.full_name,
        "email": node.email,
        "job_title": node.job_title,
        "directs": [tree_to_dict(child) for child in node.children],
    }


#
# Program Main Execution
#

# Configure logging
logging.basicConfig(
    filename=f"{BASE_DIR}/{LOG_FILE_NAME}",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

start_time = time.time()

org_tree = build_org_tree(BIG_BOSS_ID, COOKIE_HEADER)

end_time = time.time()

duration = end_time - start_time

print_tree(org_tree)

# Save to JSON file
with open(f"{BASE_DIR}/{OUTPUT_FILE_NAME}", "w") as file:
    json.dump(tree_to_dict(org_tree), file, indent=4)

print(f"Scraping all the data took: {duration}")
logging.info(f"Scraping all the data took: {duration}")

logging.info("ALL DONE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
