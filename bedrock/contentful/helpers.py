# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Helper code to change Contentful CDN URLs to relative local paths.

Assumes ou've already got the images in the codebase.

Usage:

>>> from bedrock.contentful.helpers import switch_image_urls_to_local
>>> switch_image_urls_to_local()


"""

import re
import sys
from collections import defaultdict

from bedrock.contentful.constants import CONTENT_TYPE_PAGE_RESOURCE_CENTER
from bedrock.contentful.models import ContentfulEntry

# Renames image urls like the following to be local paths:
#   "https://images.ctfassets.net/w5er3c7zdgmd/7cTC9dTpbRjoeNn3qwNbv2/63b89449a26f88b9de617f0ff0fa5acf/image2.png?w=688"
#   "https://images.ctfassets.net/w5er3c7zdgmd/7cTC9dTpbRjoeNn3qwNbv2/63b89449a26f88b9de617f0ff0fa5acf/image2.png?w=1376 1.5x"
#
# Note that some of them appear in srcset attributes, hence have the density multiplier,
# and some have width querystrigs, both of which must be catered for in the renaming.
#
# The actual files have been downloaded and added to the Bedrock codebase in the
# same changeset as this data migration will be immediately available upon deployment

contentful_cdn_images_pattern = re.compile(
    r"\"https:\/\/images\.ctfassets\.net\/"  # CDN hostname
    r"\S*"  # any path without a space
    r"(?:\s1\.5x){0,1}"  # but allow a space at the end IFF it's before '1.5x' (in a non-capturing group)
    r"\""  # and ending in a quote
)


def _print(args):
    sys.stdout.write(args)
    sys.stdout.write("\n")


def _url_to_local_filename(url):
    # Temporarily shelve any density info picked up from the src attribute. 1.5x is the only one used.
    dpr_multiplier = " 1.5x"

    if dpr_multiplier in url:
        has_dpr = True
        url = url.replace(dpr_multiplier, "")
    else:
        has_dpr = False

    base_filename = url.split("/")[-1]
    parts = base_filename.split("?")
    if len(parts) == 1:
        filename = parts[0]
    else:
        split_filename = parts[0].split(".")
        if len(split_filename) == 2:
            name, suffix = split_filename
        else:
            # filename has multiple . in it
            name = ".".join(split_filename[:-1])
            suffix = split_filename[-1]

        filename = f"{name}_{''.join(parts[1:])}.{suffix}"
        filename = filename.replace("=", "")

    if has_dpr:
        filename = f"{filename}{dpr_multiplier}"
    return filename


def switch_image_urls_to_local():
    resource_center_pages = ContentfulEntry.objects.filter(
        content_type=CONTENT_TYPE_PAGE_RESOURCE_CENTER,
    )
    for page in resource_center_pages:
        # Some safety checks. If these fail, the migration breaks and it gets rolled back

        if page.slug != "unknown":
            _print(f"Checking page {page.contentful_id} {page.slug} [{page.locale}]")
        # First the "SEO" images, which are also used on the listing page
        assert "info" in page.data

        if "seo" in page.data["info"] and "image" in page.data["info"]["seo"]:
            _print(f"Updating SEO image URL for {page.contentful_id}. Slug: {page.slug}")

            image_url = page.data["info"]["seo"]["image"]
            updated_image_url = f"/media/img/products/vpn/resource-center/{_url_to_local_filename(image_url)}"
            page.data["info"]["seo"]["image"] = updated_image_url

            _print("Saving SEO info changes\n")
            page.save()

        # Now check for images in the body of the page
        assert len(page.data["entries"]) == 1
        assert "body" in page.data["entries"][0]

        body = page.data["entries"][0]["body"]
        old_to_new = defaultdict(str)
        matches = re.findall(contentful_cdn_images_pattern, body)

        if matches:
            _print(f"Found {len(matches)} URLs to update")
            for link in matches:
                old_to_new[link] = f'"/media/img/products/vpn/resource-center/{_url_to_local_filename(link[1:-1])}"'

            for old, new in old_to_new.items():
                body = body.replace(old, new)

            page.data["entries"][0]["body"] = body
            _print("Saving page changes\n")
            page.save()
        else:
            if page.slug != "unknown":
                _print("No changes needed to page body\n")
