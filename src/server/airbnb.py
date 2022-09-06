from http import cookies
import json
import sys
import asyncio
from urllib.parse import urlencode
from quart import jsonify, Quart

import aiohttp
from bs4 import BeautifulSoup
import re
import urllib.parse


def read_file():
    with open("asdf.json", "r+") as f:
        js = json.load(f)
    f.close()
    return js


def write_file(data):
    with open('asdf.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(data))
    f.close()


async def req(url, headers):
    retries = 3
    data = ""

    print(url + "?" + urlencode(headers).replace(" ", ""))

    async with aiohttp.ClientSession(headers=headers) as session:
        for _ in range(retries):
            response = await session.get(url=url, params=headers, data=data)
            if response.status == 200:
                res = await response.text()
                # write_file(res)
                return res
            else:
                # await asyncio.sleep(sleep)
                # print("response.status")
                # print(response.status)
                # print("no response")
                raise Exception('No Response')


async def scrape():
    url_base = "https://www.airbnb.com"

    city = "Madrid"
    url_search = f"{url_base}/s/{city}/homes"

    # todo: get from html
    page_max = 30  # rn just in case so it doesnt go forever
    page = 0

    # 20 items per page -> increase by 20
    offset = 0

    # airbnb main content section follows some weird pattern of not having ids, only minified cls names:
    #   (could also use custom tags and attributes eg. itemprop)
    # todo: find out if "css modules" ids change on recompile.. its a sha of 4 dgt num but idk if the 4 dgt r random
    #   if they do chnces r cls names change but elems stay in same position in dom tree --> optimize for that in dom al lib
    grid_elem_cls = "c4mnd7m"
    grid_elem_info_cls = "g1tup9az"
    #   in grid_elem_info
    price_cls = "_tt122m"
    title_cls = "t1jojoys"
    link_cls = "ln2bl2p"  # also meta tag w link available

    # todo: check some of these headers
    headers_search = {
        "tab_id": "home_tab",
        "refinement_paths[]": "/homes",
        "flexible_trip_lengths[]": "one_week",
        "price_filter_input_type": "0",
        "query": "Madrid",
        "place_id": "ChIJgTwKgJcpQg0RaSKMYcHeNsQ",
        "date_picker_type": "calendar",
        "checkin": "2022-09-20",
        "checkout": "2022-09-27",
        "adults": "2",
        "source": "structured_search_input_header",
        "search_type": "filter_change",
        "price_filter_num_nights": "7",
        # creates a square on the map in which it is searched
        # todo: option to set location and distance. default it d have some pythagoras type inaccuarcy... could search iteratively but not that important tbh
        #   || just get location myself n calculate distance
        "ne_lat": "40.43489467364251",
        "ne_lng": "-3.672587303293966",
        "sw_lat": "40.408256752583476",
        "sw_lng": "-3.729378610582188",
        "zoom": "16",
        "search_by_map": "true",
        "room_types": "]=Entire home/apt",
        "min_beds": "2",
        "price_max": "161",
        "federated_search_session_id": "c74310b0-3b44-4290-add0-5348e572c794",
        "pagination_search": "true",
        # "items_offset": f"{offset}",
        "items_offset": "0",
        "section_offset": "2",
        # "display_currency": "EUR", # useless
    }

    # CURRENCY
    #   url param: display_currency=EUR does nth also
    #   country and currency cookie do nth.
    #   probably need to capture some session ids
    #

    # # cookie which is resbonsible for currency, needs to be encoded as str
    # user_attributes = '''{
    #     "curr": "EUR",
    #     "guest_exchange": 1.007895,
    #     "device_profiling_session_id": "1662470509--7b75d9b5815dcb2a6538c6dd",
    #     "giftcard_profiling_session_id": "1662470509--bf3af96809c4de8a42be6ee7",
    #     "reservation_profiling_session_id": "1662470509--b1c251b9c8ad5d37d846c07b"
    # }'''

    user_attributes = ('''{
        "curr": "EUR",
        "guest_exchange": 1.007895,
        "reservation_profiling_session_id": "1662470509--b1c251b9c8ad5d37d846c07b"'''  # THIS is needed for EUR but session gon be invalid tomorrow...
                       '}')

    # all cookies:
    # "cookie": "OptanonAlertBoxClosed=NR; country=AT; cdn_exp_7b27e8582f6ea5b25=treatment; cdn_exp_664025b35de9ca5f8=treatment; cdn_exp_d92fdc77c0b0762c0=control; bev=1662474545_NTNiYTI2NDU2ZWZi; cdn_exp_b910f64ca3b409af4=treatment; cdn_exp_edca6a5ab9666c814=control; cdn_exp_fea7ec9bd22598e31=control; cdn_exp_29e65ed560e5fd9f1=treatment; ak_bmsc=4702FF1A4081BFF1F2F79350FD841044~000000000000000000000000000000~YAAQk1gWAvFiI/OCAQAArGg0ExGsFjLCmGev+M3bswB/2zhpBXpbWOWrN5ig2mFSm/WUpLRj5MzUzLg0ZnzmmO1rJ3GWEkGcYRBo+dG3sdVoAmC9cbXP/hdOs+yvJ5UbJg5M5KPrRbJU32EicQhsT74VLqGLc6dyHeH5UPwmq1ejtmKjPmqyWIqwT5e3KE1fMlH9q/PeftGKrDhcc8cGgMoyJX2cvYKOzhlbGUtL/aWgd79uvfQobPCPcPrpBRqk/7Of/iQ0oyBxWvDsC6/bSjNqv4+JAzviEFWyxP8xwTgvjXizKk0xEQnAqRNIiIKbaf9i7qbqH6dP0oYJ8kc6rzSFDx9j1vSHo9Eaq2ND/7XF1F6JwLxNzZg0s/B6T9bCIxrulpJhXMdiUw==; previousTab=%7B%22id%22%3A%220ecd05f7-98c3-445a-9f48-c2d6b4050d06%22%2C%22url%22%3A%22https%3A%2F%2Fwww.airbnb.com%2Fs%2FMadrid%2Fhomes%3Ftab_id%3Dhome_tab%26refinement_paths%255B%255D%3D%252Fhomes%26flexible_trip_lengths%255B%255D%3Done_week%26price_filter_input_type%3D0%26query%3DMadrid%26place_id%3DChIJgTwKgJcpQg0RaSKMYcHeNsQ%26date_picker_type%3Dcalendar%26checkin%3D2022-09-20%26checkout%3D2022-09-27%26adults%3D2%26source%3Dstructured_search_input_header%26search_type%3Dfilter_change%26price_filter_num_nights%3D7%26ne_lat%3D40.43489467364251%26ne_lng%3D-3.672587303293966%26sw_lat%3D40.408256752583476%26sw_lng%3D-3.729378610582188%26zoom%3D16%26search_by_map%3Dtrue%26room_types%3D%255D%253DEntire%2520home%252Fapt%26min_beds%3D2%26pagination_search%3Dtrue%26items_offset%3D0%26section_offset%3D2%26display_currency%3DAUD%22%7D; everest_cookie=1662474545.QXiWh_DGT7g3Ql_RszpJ.USKbaK7UXNEG2R92x3WN7uReOjrOu0NMK8j6jzG2YQs; _csrf_token=V4%24.airbnb.com%24KEqXMdwRbX4%24nI3mgLDQBvk-9uzDRbM2bdbXiWTsnWQWl6bD_VJPy8U%3D; jitney_client_session_created_at=1662474545; _user_attributes=%7B%22curr%22%3A%22EUR%22%2C%22guest_exchange%22%3A1.007895%2C%22device_profiling_session_id%22%3A%221662474545--c72adcc30448960717f7b01d%22%2C%22giftcard_profiling_session_id%22%3A%221662474545--1b4a0fa7d3d9827a29e8f0d6%22%2C%22reservation_profiling_session_id%22%3A%221662474545--c5dc75aa5d7c2bcbb2cb0377%22%7D; flags=0; tzo=120; frmfctr=wide; jitney_client_session_id=d45cbacc-3c50-4171-81e3-bb69eb0d4288; cfrmfctr=MOBILE; cbkp=2; jitney_client_session_updated_at=1662474547; bm_sv=16B45C643D30508343ADCC0FCEC7C28F~YAAQk1gWAnhjI/OCAQAAC6o0ExEb9DU9c0RepSH3qn1bFzAm9NdUA7dzuY322lOozlWzUPTu3zHUR8USLMeCcvwFmYGnotDr2gBVssTcw3ukL4t0WvtYiWstvGuCGdjgrX8ViqwqaWMR1SeNlpkuQDn4acWEjNr4gfk9kiOIL1xsncM/znM5XnRNH3+Acv/zV066fcOjRoAoJCPsiA53VVCaQUsmnw0uEhjAy39Jc4ok6VTGHIHKIvNkVoTlxnUa~1"

    # country and currency cookie do nth.
    # "cookie": "country=AT;tzo=120;currency=EUR"

    # doesnt work
    # "cookie": "_user_attributes=curr=EUR&guest_exchange=1.007895&device_profiling_session_id=1662470509--7b75d9b5815dcb2a6538c6dd&giftcard_profiling_session_id=1662470509--bf3af96809c4de8a42be6ee7&reservation_profiling_session_id=1662470509--b1c251b9c8ad5d37d846c07b"

    # this works
    # "cookie": '_user_attributes=%7B%22curr%22%3A%22EUR%22%2C%22guest_exchange%22%3A1.007895%2C%22device_profiling_session_id%22%3A%221662470509--7b75d9b5815dcb2a6538c6dd%22%2C%22giftcard_profiling_session_id%22%3A%221662470509--bf3af96809c4de8a42be6ee7%22%2C%22reservation_profiling_session_id%22%3A%221662470509--b1c251b9c8ad5d37d846c07b%22%7D'

    # headers_search['cookie'] = f"_user_attributes={urllib.parse.quote(user_attributes)}"

    # ----------------

    room_id = 1
    url_rooms = f"{url_base}/{room_id}"
    # /rooms / 33062412?adults = 2 & check_in = 2022 - 09 - 20 & check_out = 2022 - 09 - 27 & previous_page_section_name = 1000 & federated_search_id = 378ad01a - 5374 - 4bf3 - a518 - 1076946159cb
    headers_rooms = {
        "adults": "2",
        "check_in": "2022-09-20",
        "check_out": "2022-09-27",
        # "previous_page_section_name": "1000",
        # "federated_search_id": "378ad01a-5374-4bf3-a518-1076946159cb"
    }
    # tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&price_filter_input_type=0&query=Madrid&place_id=ChIJgTwKgJcpQg0RaSKMYcHeNsQ&date_picker_type=calendar&checkin=2022-09-20&checkout=2022-09-27&adults=2&source=structured_search_input_header&search_type=filter_change&price_filter_num_nights=7&ne_lat=40.43489467364251&ne_lng=-3.672587303293966&sw_lat=40.408256752583476&sw_lng=-3.729378610582188&zoom=16&search_by_map=true&room_types%5B%5D=Entire%20home%2Fapt&min_beds=2&price_max=161&federated_search_session_id=c74310b0-3b44-4290-add0-5348e572c794&pagination_search=true&items_offset=20&section_offset=2"

    data = []
    while page <= page_max:

        print(url_search)

        print(headers_search['items_offset'])

        html = await req(url_search, headers=headers_search)

        soup = BeautifulSoup(html, features="html.parser")
        # get grid_elements from grid listing:

        grid_elements = soup.find_all("div", {"class": grid_elem_cls})

        # # unnecessary checks if i d have the len...
        if page > page_max:
            raise "shouldn have this many pages"

        # if len(grid_elements) < 20 and page != page_max:
        #     raise ("not enough items found on page")

        if not len(grid_elements):
            break

        for elem in grid_elements:
            # there should only be one (atleast in the context of the grid elem) if not then grid_elem_info
            #  could have just directly searched for that class
            # asdfsdf
            # but could be helpful to improve "change resistance" in the future
            # also reduce chance of title etc. mismatch bc some other grid_elements could have classes used outside of the grid elem

            grid_elem_info_divs = elem.find_all("div", {"class": price_cls})

            # info fields
            price_divs = elem.find_all("div", {"class": price_cls})
            title_divs = elem.find_all("div", {"class": title_cls})
            link_divs = elem.find_all("a", {"class": link_cls})

            # ensure theres exactly 1 found w this cls
            for unique_elem in [
                    price_divs,
                    title_divs,
                    link_divs
            ]:
                if len(unique_elem) != 1:
                    raise "invalid or ambiguous cls name for " + unique_elem

            # some prices in list dont match at all when u open the link. but total price seems to be correct.
            # todo: open link and assert total price
            price_txt = price_divs[0].span.text
            price = re.search(
                "\$([\d,]*) ", price_txt).group(1).replace(",", "")

            title = title_divs[0].text
            link = link_divs[0]['href']  # local link: /rooms/....

            # print(title)
            # print(price)
            # print(price_divs[0])
            m = re.search("\/rooms\/(\d*)\?", str(link))

            # todo check for all n write err in table or throw idk

            # if m.group(1):
            #     room_id = m.group(1)
            # else:
            #     raise "asdf"
            # print(room_id)

            data_elem = {
                "id": room_id,
                "title": title,
                "link": f"{url_base}/{link}",
                "price": price
            }

            data.append(data_elem)

            # todo: get room id call room page, get location, calc distance to center

        page += 1
        offset += 20
        headers_search['items_offset'] = str(offset)
    write_file(data)
    return data


# todo: check current state of async py - i think at this point there might be better alternatives than aiohttp and maybe quart
# asyncio err "event loop is closed"
# https://github.com/encode/httpx/issues/914#issuecomment-622586610-permalink

# if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# asyncio.run(scrape())
