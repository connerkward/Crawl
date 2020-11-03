import requests
import cbor
import time

from utils.response import Response

def download(url, config, logger=None):
    # Has been edited from original
    try:
        host, port = config.cache_server
        resp = requests.get(
            f"http://{host}:{port}/",
            params=[("q", f"{url}"), ("u", f"{config.user_agent}")])
        if len(resp.content) == 0: # added due to "ValueError: got zero length string in loads"
            return Response({"url": "", "status": 404, "error": ""})
        if resp:
            return Response(cbor.loads(resp.content))
    except EOFError or ValueError:  # "ValueError: got zero length string in loads"
        return Response({"url": "", "status": 404, "error": ""})
    logger.error(f"Spacetime Response error {resp} with url {url}.")
    return Response({
        "error": f"Spacetime Response error {resp} with url {url}.",
        "status": resp.status_code,
        "url": url})
