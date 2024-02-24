#!/usr/bin/env python3

import argparse
import asyncio
import base64
import logging
import os
import re
import shutil
import tempfile
import unicodedata
from hashlib import md5
from urllib.parse import urlparse

import aiohttp
import requests
import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

logger = logging.getLogger("update_lists")
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(funcName)s - %(levelname)s - %(message)s",
)

sentry_sdk.init(enable_tracing=False)


# https://github.com/django/django/blob/4fec1d2ce37241fb8fa001971c441d360ed2a196/django/utils/text.py#L436-L453
def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "_", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Tool to download the lists for an Adblock catalog"
    )
    parser.add_argument(
        "--adblock-catalog",
        type=str,
        help="the URL of the Adblock catalog",
        default="https://raw.githubusercontent.com/brave/adblock-resources/master/filter_lists/list_catalog.json",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="the directory to save the downloaded lists",
        default="lists",
    )
    return parser.parse_args()


def validate_checksum(filename):
    """Validate the checksum header"""
    data = open(filename, "rb").read().decode("utf-8")

    # Extract and remove checksum
    checksum_pattern = re.compile(
        r"^\s*!\s*checksum[\s\-:]+([\w\+\/=]+).*\n", re.MULTILINE | re.IGNORECASE
    )
    match = checksum_pattern.search(data)
    if not match:
        logger.warn(f"Couldn't find a checksum in {filename}")
        return

    checksum = match.group(1)
    data = checksum_pattern.sub("", data, 1)

    # Normalize data
    data = re.sub(r"\r", "", data)
    data = re.sub(r"\n+", "\n", data)

    # Calculate new checksum
    checksum_expected = md5(data.encode("utf-8")).digest()
    checksum_expected = base64.b64encode(checksum_expected).decode().rstrip("=")

    # Compare checksums
    if checksum == checksum_expected:
        logging.info(f"Checksum is valid: {filename}")
    else:
        raise Exception(
            f"Wrong checksum, found {checksum}, expected [{checksum_expected}] in {filename}"
        )


def move_downloaded_file(filename, url, output_dir):
    """
    Moves the downloaded file to the appropriate location in the output directory.

    Args:
        filename (str): The name of the downloaded file.
        url (str): The URL from which the file was downloaded.
        output_dir (str): The directory where the file should be moved.

    Returns:
        str: The path of the moved file.

    Notes:
        The destination path is derived from the URL. The filename is extracted from the URL
        and appended to the output directory path to determine the final destination of the file.
    """
    parsed_url = urlparse(url)
    url_path = parsed_url.path
    url_dir = "/".join(parsed_url.path.split("/")[:-1]).lstrip(
        "/"
    )  # uBlockOrigin/uAssets/master/filters
    local_dir = os.path.join(
        output_dir, parsed_url.scheme, parsed_url.hostname, url_dir
    )  # https/raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters
    os.makedirs(local_dir, exist_ok=True)
    output_file_name = os.path.basename(url_path) + slugify(parsed_url.query)
    output_file_path = os.path.join(
        local_dir, output_file_name
    )  # https/raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/filters.txt

    try:
        validate_checksum(filename)
        logger.info(f"moving {filename} to {output_file_path}")
        shutil.move(filename, output_file_path)
    except Exception as e:
        logger.exception(f"An exception happened while processing {filename}")
        os.remove(filename)
    return output_file_path


async def fetch_and_save_url(url, output_dir):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, raise_for_status=True) as response:
                # Check if the response is successful
                if response.status == 200:
                    # Create a temporary file
                    temp_file = tempfile.NamedTemporaryFile(delete=False)

                    # Write the response content to the temporary file
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        temp_file.write(chunk)
                    temp_file.close()
                    logger.info(f"downloaded {url}")

                    move_downloaded_file(temp_file.name, url, output_dir)
        except (
            aiohttp.ClientResponseError,
            aiohttp.client_exceptions.ClientConnectorError,
        ) as e:
            logging.exception(f"An exception happened while processing {url}")


async def main():
    args = parse_arguments()

    adblock_catalog = requests.get(args.adblock_catalog, timeout=60).json()

    adblock_lists = []
    for al in adblock_catalog:
        for src in al["sources"]:
            adblock_lists.append(src["url"])
    from pprint import pprint

    return await asyncio.gather(
        *[fetch_and_save_url(url, args.output_dir) for url in adblock_lists]
    )


if __name__ == "__main__":
    asyncio.run(main())