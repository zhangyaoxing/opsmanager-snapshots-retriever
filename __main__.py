from ConfigParser import SafeConfigParser
from requests.auth import HTTPDigestAuth
import requests
import logging
import datetime
import json

REQ_PAGE_SIZE=100

def get_api_result(parser, uri):
    base_url = parser.get("config", "base_url")
    username = parser.get("config", "username")
    api_key = parser.get("config", "api_key")
    logger = logging.getLogger(__name__)

    if not base_url.endswith("/"):
        base_url += "/"
    page = 1
    all_results = []
    while 1:
        url = '{0}{1}?pageNum={2}&itemsPerPage={3}'.format(base_url, uri, page, REQ_PAGE_SIZE)
        logger.debug(url)
        r = requests.get(url, auth=HTTPDigestAuth(username, api_key))
        if r.status_code != 200:
            logger.error("Error requesting Ops Manager API!")
            logger.error("Raw response from server: {0}".format(r.text))
            exit()
        result = r.json()
        logger.debug(result)
        for r in result["results"]:
            all_results.append(r)
        
        if (result["totalCount"] < page * REQ_PAGE_SIZE):
            break
        page += 1

    return all_results


def get_groups(parser):
    logger = logging.getLogger(__name__)
    uri = "api/public/v1.0/groups"
    results = get_api_result(parser, uri)
    gids = []
    for r in results:
        gids.append(r["id"])
    logger.info("All groups found: {0}".format(gids))

    return gids

def get_clusters(parser, gids):
    logger = logging.getLogger(__name__)
    cids = []
    for gid in gids:
        uri = "api/public/v1.0/groups/{0}/clusters".format(gid)
        results = get_api_result(parser, uri)
        for c in results:
            del c["links"]
            cids.append(c)
    logger.info("All clusters found: {0}".format(cids))

    return cids

def get_snapshots(parser, cids):
    logger = logging.getLogger(__name__)
    snapshots = []
    for cid in cids:
        uri = "api/public/v1.0/groups/{0}/clusters/{1}/snapshots".format(cid["groupId"], cid["id"])
        results = get_api_result(parser, uri)
        cid["snapshots"] = []
        for s in results:
            del s["links"]
            cid["snapshots"].append(s)
        logger.info("{0} snapshot(s) found for cluster {1}".format(len(results), cid["id"]))
    
    return cids

if __name__ == "__main__":
    parser = SafeConfigParser()
    parser.read('config.ini')
    level = parser.get("config", "log_level")

    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    logger.info("Connecting to Ops Manager: {0}".format(parser.get("config", "base_url")))
    logger.info("Getting all groups...")
    gids = get_groups(parser)
    cids = get_clusters(parser, gids)
    snapshots = get_snapshots(parser, cids)

    filename = parser.get("config", "output_file").format(datetime.datetime.now().isoformat())
    with open(filename, 'wb') as outfile:
        json.dump(snapshots, outfile)
    logger.info("Snapshot info output to: {0}".format(filename))