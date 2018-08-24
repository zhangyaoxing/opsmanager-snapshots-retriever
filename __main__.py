from ConfigParser import SafeConfigParser
from requests.auth import HTTPDigestAuth
import requests
import logging

REQ_PAGE_SIZE=100

def get_groups(parser):
    base_url = parser.get("config", "base_url")
    username = parser.get("config", "username")
    api_key = parser.get("config", "api_key")
    logger = logging.getLogger(__name__)

    if not base_url.endswith("/"):
        base_url += "/"
    page = 1
    group_ids = []
    while 1:
        url = '{0}api/public/v1.0/groups?pageNum={1}&itemsPerPage={2}'.format(base_url, page, REQ_PAGE_SIZE)
        logger.debug(url)
        r = requests.get(url, auth=HTTPDigestAuth(username, api_key))
        if r.status_code != 200:
            logger.error("Error requesting Ops Manager API!")
            logger.error("Raw response from server: {0}".format(r.text))
            exit()
        result = r.json()
        logger.debug(result)
        for r in result["results"]:
            group_ids.append(r["id"])
        
        if (result["totalCount"] < page * REQ_PAGE_SIZE):
            break
        page += 1
        
    logger.debug("All groups found: {0}".format(group_ids))

if __name__ == "__main__":
    parser = SafeConfigParser()
    parser.read('config.ini')
    level = parser.get("config", "log_level")

    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    logger.info("Connecting to Ops Manager: {0}".format(parser.get("config", "base_url")))
    logger.info("Getting all groups...")
    get_groups(parser)