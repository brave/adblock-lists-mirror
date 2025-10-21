#!/usr/bin/env python3

import argparse
import asyncio
import base64
import ipaddress
import json
import logging
import os
import re
import shutil
import tempfile
import unicodedata
import hashlib
from typing import Optional, Tuple
from urllib.parse import urlparse

import aiohttp
import requests
import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

# Security constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
CHUNK_SIZE = 1024 * 16  # 16KB chunks
ALLOWED_SCHEMES = {'https'}
BLACKLISTED_DOMAINS = {
    'localhost', '127.0.0.1', '::1', '0.0.0.0',
    '169.254.169.254'  # AWS metadata service
}
PRIVATE_IP_RANGES = [
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('fd00::/8')
]

MAX_RETRIES = 3
RETRY_DELAY = 2  
BACKOFF_MULTIPLIER = 2

logger = logging.getLogger("update_lists")
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(funcName)s - %(levelname)s - %(message)s",
)

sentry_sdk.init(enable_tracing=False)


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
    data = re.sub(r"\n+\Z", "\n", data)

    # Calculate new checksum
    checksum_expected = hashlib.md5(data.encode("utf-8")).digest()
    checksum_expected = base64.b64encode(checksum_expected).decode().rstrip("=")

    # Compare checksums
    if checksum == checksum_expected:
        logging.info(f"Checksum is valid: {filename}")
    else:
        raise Exception(
            f"Wrong checksum, found {checksum}, expected [{checksum_expected}] in {filename}"
        )


def is_private_ip(ip: str) -> bool:
    """Check if an IP address is in private ranges."""
    try:
        addr = ipaddress.ip_address(ip)
        if addr.is_private:
            return True
        return any(addr in network for network in PRIVATE_IP_RANGES)
    except ValueError:
        return False


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a URL before downloading.
    
    Args:
        url: The URL to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ALLOWED_SCHEMES:
            return False, f"Invalid scheme: {parsed.scheme}. Only HTTPS is allowed."
            
        # Check for IP addresses in hostname
        try:
            if is_private_ip(parsed.hostname):
                return False, "Access to private IP addresses is not allowed"
        except (ValueError, AttributeError):
            pass
            
        # Check blacklisted domains
        if parsed.hostname in BLACKLISTED_DOMAINS:
            return False, f"Access to {parsed.hostname} is not allowed"
            
        # Check for basic URL format
        if not all([parsed.scheme, parsed.netloc]):
            return False, "Invalid URL format"
            
        return True, None
        
    except Exception as e:
        return False, f"URL validation failed: {str(e)}"


def move_downloaded_file(filename: str, url: str, output_dir: str) -> Optional[str]:
    """
    Moves the downloaded file to the appropriate location in the output directory.

    Args:
        filename: The name of the downloaded file.
        url: The URL from which the file was downloaded.
        output_dir: The directory where the file should be moved.

    Returns:
        The path of the moved file, or None if an error occurred.
    """
    try:
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Temporary file {filename} not found")
            
        # Skip checksum for EasyList URLs
        if not url.startswith("https://easylist-downloads.adblockplus.org/"):
            try:
                validate_checksum(filename)
            except Exception as e:
                logger.error(f"Checksum validation failed for {url}: {str(e)}")
                os.remove(filename)
                return None

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output filename
        output_file_name = hashlib.md5(url.encode('utf-8')).hexdigest() + '.txt'
        output_file_path = os.path.join(output_dir, output_file_name)
        
        # Move the file
        shutil.move(filename, output_file_path)
        logger.info(f"Moved {url} to {output_file_path}")
        return output_file_path
        
    except Exception as e:
        logger.exception(f"Error processing {url}")
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except OSError:
                pass
        return None


async def fetch_and_save_url(url: str, output_dir: str) -> bool:
    """
    Download a file from a URL and save it to the output directory with retry logic.
    
    Args:
        url: The URL to download from
        output_dir: Directory to save the downloaded file
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Validate URL first
    is_valid, error_msg = validate_url(url)
    if not is_valid:
        logger.error(f"URL validation failed for {url}: {error_msg}")
        return False

    for attempt in range(MAX_RETRIES):
        temp_file = None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, raise_for_status=True, timeout=aiohttp.ClientTimeout(total=300)) as response:
                    if response.status == 200:
                        temp_file = tempfile.NamedTemporaryFile(delete=False)
                        total_size = 0
                        
                        try:
                            while True:
                                chunk = await response.content.read(CHUNK_SIZE)
                                if not chunk:
                                    break
                                    
                                # Check file size limit
                                total_size += len(chunk)
                                if total_size > MAX_FILE_SIZE:
                                    raise ValueError(
                                        f"File size exceeds maximum allowed size of {MAX_FILE_SIZE} bytes"
                                    )
                                    
                                temp_file.write(chunk)
                                
                            temp_file.close()
                            logger.info(f"Downloaded {total_size} bytes from {url}")
                            
                            # Move file and return success
                            if move_downloaded_file(temp_file.name, url, output_dir):
                                return True
                            else:
                                logger.error(f"Failed to move downloaded file for {url}")
                                return False
                                
                        except Exception as e:
                            if temp_file and os.path.exists(temp_file.name):
                                temp_file.close()
                                os.unlink(temp_file.name)
                            raise e
                            
        except (aiohttp.ClientResponseError, aiohttp.ClientConnectorError, aiohttp.ServerDisconnectedError) as e:
            logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} failed for {url}: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAY * (BACKOFF_MULTIPLIER ** attempt)
                logger.info(f"Retrying {url} in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"All {MAX_RETRIES} attempts failed for {url}: {str(e)}")
        except asyncio.TimeoutError:
            logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} timed out for {url}")
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAY * (BACKOFF_MULTIPLIER ** attempt)
                logger.info(f"Retrying {url} in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"All {MAX_RETRIES} attempts timed out for {url}")
        except Exception as e:
            logger.error(f"Unexpected error processing {url}: {str(e)}")
            break
        finally:
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except OSError:
                    pass
    
    return False


async def main():
    args = parse_arguments()

    try:
        adblock_catalog = requests.get(args.adblock_catalog, timeout=60).json()
    except Exception as e:
        logger.error(f"Failed to fetch adblock catalog: {str(e)}")
        return

    adblock_lists = []
    metadata = {}
    for al in adblock_catalog:
        for src in al["sources"]:
            url = src["url"]
            adblock_lists.append(url)
            metadata[hashlib.md5(url.encode('utf-8')).hexdigest()] = url

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    metadata_file = os.path.join(args.output_dir, 'metadata.json')
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=4)

    logger.info(f"Starting download of {len(adblock_lists)} lists...")
    
    # Download all lists and collect results
    results = await asyncio.gather(
        *[fetch_and_save_url(url, args.output_dir) for url in adblock_lists],
        return_exceptions=True
    )
    
    # Count successes and failures
    successful = sum(1 for result in results if result is True)
    failed = len(results) - successful
    
    logger.info(f"Download completed: {successful} successful, {failed} failed out of {len(adblock_lists)} total")
    
    if failed > 0:
        logger.warning(f"{failed} downloads failed, but continuing with available lists")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
