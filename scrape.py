import requests
import pandas as pd
import csv
import os

# -------Direct API Requests - Extraction of raw data------- #

def fetch_locals_from_comelec(code, name):
    ''' Fetches the JSON data for the Regional down to baranggay level data. '''
    
    url = f"https://2025electionresults.comelec.gov.ph/data/regions/local/{code}.json"

    payload = {}
    headers = {
        'Cookie': '__cf_bm=dodswbwnKOQkXT6kGyV5hLFBczyHlWBFAg7P.Mq6dR8-1747135983-1.0.1.1-5gWqGu78cTooG.DZ91TAvT5YOQHCc6n1lhirFiq064M80KYfYva.HyXpMY9ebkMcxC4wKn7h4dTgYJZBmvl1G9wGa599RmG4nXo.VWKGHCQ',
        'sec-ch-ua-platform': 'Windows',
        'Referer': 'https://2025electionresults.comelec.gov.ph/er-result',
        'sec-ch-ua': 'Chromium;v=136, Microsoft',
        'sec-ch-ua-mobile': '?0'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    
    if response.status_code != 200:
        data = {}
    else:
        data = response.json()['regions']
        
    print(f"[{response.status_code}] {code} - {name}: Fetched {len(data)} records")

    return data



def fetch_precincts_from_comelec(code, name):
    ''' 
    Fetches the JSON data for the precinct-level data. 
    The request URL structure is quite different from the regional to baranggay data. 
    '''

    url = f"https://2025electionresults.comelec.gov.ph/data/regions/precinct/{code[:2]}/{code}.json"

    payload = {}
    headers = {
    'accept-language': 'en-US,en;q=0.9',
    'if-modified-since': 'Tue, 13 May 2025 12:50:19 GMT',
    'if-none-match': 'W/38c86a4b725b8f16a24b7d650f0d1a21',
    'priority': 'u=1, i',
    'referer': 'https://2025electionresults.comelec.gov.ph/er-result',
    'sec-ch-ua': 'Chromium;v=136, Microsoft',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': 'Windows',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code != 200:
        data = {}
    else:
        data = response.json()['regions']
        
    print(f"[{response.status_code}] {code} - {name}: Fetched {len(data)} records")

    return data

def fetch_er_data(code):
    ''' Fetches the JSON data for the precinct vote counts. '''

    url = f"https://2025electionresults.comelec.gov.ph/data/er/{code[:3]}/{code}.json"

    payload = {}
    headers = {
    'accept-language': 'en-US,en;q=0.9',
    'priority': 'u=1, i',
    'referer': 'https://2025electionresults.comelec.gov.ph/er-result',
    'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code != 200:
        data = {}
        print(f"[{response.status_code}] Precinct {code}: no data found")
    else:
        data = response.json()
        print(f"[{response.status_code}] Precinct {code} - {data['information']['precinctInCluster']}: OK")
        
    return data


# -------Extracting the granular data (Geographical)------- #

# Fetch the regions
def get_regional_data():
    ''' Initialize the top level list, outputs the regional-level data. '''

    regions = fetch_locals_from_comelec('0', 'region')
    pd.DataFrame(regions).to_csv('regions.csv')

    return regions

# Loop through the regions and get the province codes, etc.
def fetch_local_data(data, target):
    ''' Loop through higher level data and drill down to fetch granular data '''

    output = []
    
    for d in data:
        category_code = d['categoryCode']
        parent_code = d['masterCode']
        current_code = d['code']
        name = d['name']

        target_data = fetch_locals_from_comelec(current_code, name)

        output.extend(target_data)
    
    print(f"{len(output)} total records")
    print(output)
    
    pd.DataFrame(output).to_csv(f"{target}.csv")

    return output

# Loop through the baranggays and get the province codes, etc.
def fetch_precinct_data():
    ''' Loop through baranggay data and drill down to fetch precint-level data. Used the csv file to avoid out of memory errors. '''

    baranggays = []
    with open('baranggays.csv', mode='r', newline='') as f:
        reader = csv.reader(f) #returns a generator
        next(reader) #skip the headers

        for row in reader:
            baranggays.append(row[3])

    with open('precincts.csv', mode='w', newline='') as f:
        columns = ['categoryCode', 'masterCode', 'code', 'name']
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()

        # Loop through the baranggays
        for baranggay in baranggays:
            current_code = baranggay
            precincts = fetch_precincts_from_comelec(current_code, 'precincts')

            for precinct in precincts:
                writer.writerow(
                    {
                        'categoryCode': None, 
                        'masterCode': current_code,
                        'code': precinct['code'],
                        'name': precinct['name']
                    }
                )

# Master function
def main():
    regions = get_regional_data()
    provinces = fetch_local_data(regions, 'provinces')
    cities = fetch_local_data(provinces, 'cities')
    baranggays = fetch_local_data(cities, 'baranggays')
    precincts = fetch_precinct_data()


# ------ETL Functions (Actual Vote counts)------- #
# Helper function
def write_csv_row(filename, columns, row):
    '''
    Helper function to avoid redundant code. Basically checks if there is an existing csv file, then writes the data in real time.

    Args:
        filename (str): path of the csv file.
        columns (iterable): list of names to be used as column headers.
        row (iterable): actual row data.

    Returns: none
    '''
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        if not file_exists or os.stat(filename).st_size == 0:
            writer.writeheader()
        writer.writerow(row)

# ETL functions
def extract_precinct_data(data):
    precinct_info = data['information']
    senator_info = data['national'][0]['statistic']
    party_info = data['national'][1]['statistic']

    row = {
        "precinct_code" : precinct_info['precinctId'],
        "precinct_cluster" : precinct_info['precinctInCluster'],
        "location" : precinct_info['location'],
        "abstentions" : precinct_info['abstentions'],
        "registered_voters" : precinct_info['numberOfRegisteredVoters'],
        "actual_voters" : precinct_info['numberOfActuallyVoters'],
        "valid_ballots" : precinct_info['numberOfValidBallot'],

        "senator_over" : senator_info['overVotes'],
        "senator_under" : senator_info['underVotes'],
        "senator_valid" : senator_info['validVotes'],
        "senator_obtained" : senator_info['obtainedVotes'],

        "party_over" : party_info['overVotes'],
        "party_under" : party_info['underVotes'],
        "party_valid" : party_info['validVotes'],
        "party_obtained" : party_info['obtainedVotes']    
    }

    columns = list(row.keys())
    write_csv_row('precinct_info.csv', columns, row)        

def extract_senator_data(data):
    precinct_code = data['information']['precinctId']
    senators = data['national'][0]['candidates']['candidates']

    columns = ['precinct_code', 'name', 'vote']

    for senator in senators:
        row = {
            'precinct_code' : precinct_code,
            'name' : senator['name'],
            'vote' : senator['votes']
        }

        write_csv_row('precinct_senators.csv', columns, row)


def extract_partylist_data(data):
    precinct_code = data['information']['precinctId']
    partylists = data['national'][1]['candidates']['candidates']

    columns = ['precinct_code', 'name', 'vote']

    for partylist in partylists:
        row = {
            'precinct_code' : precinct_code,
            'name' : partylist['name'],
            'vote' : partylist['votes']
        }

        write_csv_row('precinct_partylist.csv', columns, row)

def transform_er_data():
    # in case the scraper runs into an empty data, it can be rerun. Not needed with revised code below, though.
    with open('precinct_info.csv', mode='r', newline='') as i:
        checkpoint = len(i.readlines()) - 1 

    # Main logic    
    with open('./output/precincts.csv', mode='r', newline='') as f:
        precinct_codes = [x.split(',')[2] for x in f][1:]

    for idx, code in enumerate(precinct_codes[checkpoint:]):
        idx += checkpoint
        er_data = fetch_er_data(code)

        if not er_data:
            print(f"Extracted precinct {code} ({idx}/{len(precinct_codes)}) - No Data found")
        else:
            extract_precinct_data(er_data)
            extract_senator_data(er_data)
            extract_partylist_data(er_data)

            print(f"Extracted precinct {code} ({idx}/{len(precinct_codes)}) - Data loaded")


transform_er_data()