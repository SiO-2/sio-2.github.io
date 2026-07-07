#!/usr/bin/env python
"""
Script to fetch citation counts from Google Scholar and store them in _data/citations.yml
This script is designed to be run by a GitHub Action.
"""

import os
import sys
import yaml
import time
import random
import multiprocessing
from datetime import datetime
from scholarly import scholarly, ProxyGenerator

# Configuration
SCHOLAR_USER_ID = "BE5IQkwAAAAJ"  # Your Google Scholar ID
OUTPUT_FILE = "_data/citations.yml"
MAX_RETRIES = 2
FETCH_TIMEOUT = 35

# Create data directory if it doesn't exist
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)


def fetch_author_data(queue, http_proxy, https_proxy, skip_proxy):
    try:
        # Setup proxy
        if http_proxy or https_proxy:
            print(f"Using system proxy: {http_proxy or https_proxy}", flush=True)
            # scholarly will automatically use HTTP_PROXY/HTTPS_PROXY environment variables
        elif skip_proxy:
            print("SKIP_PROXY is set, attempting direct connection...", flush=True)
        else:
            print("Attempting to use free proxies...", flush=True)
            try:
                pg = ProxyGenerator()
                pg.FreeProxies()
                scholarly.use_proxy(pg)
            except Exception as proxy_error:
                print(f"FreeProxies failed: {proxy_error}", flush=True)
                print("Attempting direct connection...", flush=True)

        scholarly.set_timeout(30)
        author = scholarly.search_author_id(SCHOLAR_USER_ID)
        queue.put((True, scholarly.fill(author)))
    except Exception as e:
        queue.put((False, str(e)))


def get_scholar_citations():
    """
    Fetch citation data from Google Scholar for all papers by the specified author
    """
    print(f"Fetching citations for Google Scholar ID: {SCHOLAR_USER_ID}")

    # Initialize citation data structure
    citation_data = {
        "metadata": {},
        "author": {},
        "papers": {},  # Initialize as empty dict, not None
    }

    # Try to load existing data first to avoid unnecessary requests
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r") as f:
                existing_data = yaml.safe_load(f)
                if existing_data and isinstance(existing_data, dict):
                    if (
                        "metadata" in existing_data
                        and existing_data["metadata"] is not None
                    ):
                        citation_data["metadata"] = existing_data["metadata"]
                    if (
                        "author" in existing_data
                        and existing_data["author"] is not None
                    ):
                        citation_data["author"] = existing_data["author"]
                    if (
                        "papers" in existing_data
                        and existing_data["papers"] is not None
                    ):
                        citation_data["papers"] = existing_data["papers"]
        except Exception as e:
            print(f"Warning: Could not read existing citation data: {e}")

    # Check for proxy settings
    http_proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    https_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    skip_proxy = os.environ.get("SKIP_PROXY", "false").lower() == "true"
    is_ci = os.environ.get("CI", "false").lower() == "true"

    # Google Scholar blocks GitHub-hosted runners frequently. Without a proxy,
    # fail visibly instead of burning the job timeout and reusing stale data.
    if is_ci and not http_proxy and not skip_proxy:
        print("ERROR: Running in CI without HTTP_PROXY/HTTPS_PROXY.")
        print("Please set the HTTP_PROXY repository secret to update Google Scholar citations.")
        return citation_data, False

    # Fetch author data with retries
    author_data = None
    for attempt in range(MAX_RETRIES):
        queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=fetch_author_data,
            args=(queue, http_proxy, https_proxy, skip_proxy),
        )
        process.start()
        process.join(FETCH_TIMEOUT)

        try:
            if process.is_alive():
                process.terminate()
                process.join()
                raise TimeoutError(
                    f"Google Scholar fetch timed out after {FETCH_TIMEOUT}s"
                )

            if queue.empty():
                raise RuntimeError("Google Scholar fetch exited without returning data")

            success, result = queue.get()
            if not success:
                raise RuntimeError(result)

            author_data = result
            break
        except Exception as e:
            wait_time = (2**attempt) + random.uniform(0, 1)  # Exponential backoff
            print(f"Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {wait_time:.1f} seconds...")
                time.sleep(wait_time)
            else:
                print("All retries failed. Using existing data if available.")
                return citation_data, False

    if not author_data:
        print("Could not fetch author data")
        return citation_data, False

    citation_data["metadata"]["last_updated"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    if "name" in author_data:
        citation_data["author"]["name"] = author_data["name"]
    if "citedby" in author_data:
        citation_data["author"]["citedby"] = author_data["citedby"]

    # Process publications
    if "publications" in author_data:
        for pub in author_data["publications"]:
            try:
                # Get publication ID
                pub_id = None
                if "pub_id" in pub and pub["pub_id"]:
                    pub_id = pub["pub_id"]
                elif "author_pub_id" in pub and pub["author_pub_id"]:
                    pub_id = pub["author_pub_id"]

                if not pub_id:
                    print(
                        f"Warning: No ID found for publication: {pub.get('bib', {}).get('title', 'Unknown')}"
                    )
                    continue

                # Get publication metadata
                title = "Unknown Title"
                year = "Unknown Year"
                citations = 0

                if "bib" in pub:
                    if "title" in pub["bib"]:
                        title = pub["bib"]["title"]
                    if "pub_year" in pub["bib"]:
                        year = pub["bib"]["pub_year"]

                if "num_citations" in pub:
                    citations = pub["num_citations"]

                print(f"Found: {title} ({year}) - Citations: {citations}")

                # Store citation data
                citation_data["papers"][pub_id] = {
                    "title": title,
                    "year": year,
                    "citations": citations,
                }

            except Exception as e:
                print(f"Error processing publication: {str(e)}")
    else:
        print("No publications found in author data")

    return citation_data, True


if __name__ == "__main__":
    citation_data, updated = get_scholar_citations()

    if not updated:
        print(
            "Citation data was not updated because fresh Google Scholar data was not fetched."
        )
        sys.exit(1)

    # Save to YAML file
    try:
        with open(OUTPUT_FILE, "w") as f:
            yaml.dump(citation_data, f, default_flow_style=False, sort_keys=False)
        print(f"Citation data saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error saving citation data: {str(e)}")
