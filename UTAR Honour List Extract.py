import re
import ast
import csv
import urllib3
import requests
from bs4 import BeautifulSoup


outputfile = "./output.csv"
configfile = "./config.txt"

# Open file in write mode and add header (only once)
with open(outputfile, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(['NAME','ID','COURSE','STREAM','SESSION','EXAM_MONTH','PARTTIME/FULLTIME','HONOUR','LEVEL','COURSE_NAME'])  # Write header 10V

# Read the text file
with open(configfile, "r") as datafile:
    content = datafile.read()

# Extract variables
def extract(var_name, content, var_type='list'):
    pattern = rf"{var_name}=(\[[^\]]+\]|\{{[^\}}]+\}})"
    match = re.search(pattern, content)
    if match:
        data = match.group(1)
        # Safely evaluate and return the data
        return ast.literal_eval(data)
    return [] if var_type == 'list' else {}

# Extract the variables
fsession = extract("fsession", content)
fcourse = extract("fcourse", content)
fstream = extract("fstream", content, var_type='dict')
fhmonth = extract("fhmonth", content)
fpartcd = extract("fpartcd", content)
fhonour = extract("fhonour", content)
bcourse = extract("bcourse", content, var_type='dict')

# Links Generation
def get_link(fcourse=fcourse, fstream=fstream, fsession=fsession, fhmonth=fhmonth, fpartcd=fpartcd, fhonour=fhonour, bcourse=bcourse):
    updated_data = []
    for course in fcourse:
        for SID, SN in fstream.items():
            for session in fsession:
                for month in fhmonth:
                    for partcd in fpartcd:
                        for honour in fhonour:
                            flink = f"https://www2.utar.edu.my/deas/acaHonourList.jsp?fcourse={course}&fstream={SID}&fsession={session}&fhmonth={month}&fpartcd={partcd}&fhonour={honour}&flevel=F&fdesc={SN}"

                            updated_data.append(flink)
                            
    for CID, CN in bcourse.items():
        for session in fsession:
            for month in fhmonth:
                for partcd in fpartcd:
                    for honour in fhonour:
                        b_link = f"https://www2.utar.edu.my/deas/acaHonourList.jsp?fcourse={CID}&fsession={session}&fhmonth={month}&fpartcd={partcd}&fhonour={honour}&flevel=B&fdesc={CN}"
                        
                        updated_data.append(b_link)
    
    return updated_data

links = get_link()
print("Stage 1 Completed")

# Accessing Website
variables = ['fcourse','fstream','bcourse','fsession','fhmonth','fpartcd','fhonour']

for URL in links:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    r = requests.get(URL, verify=False)
    soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib

    try:
        table = soup.find('tbody')
        table = table.find('tbody')
    except:
        continue

    if table == None:
        continue

    lst=[]  # Quotes storage
    record = [] # Course info

    # Get inital URL data
    matches = re.findall(r'(?<==)([^&]+)', URL) 
    if len(matches) < 8:
        matches.insert(1, "")
    record = matches

    # Extract all info in <tr>
    rows = table.find_all('tr')
    for row in rows:
        lst.append(row.text.strip())

    # Data extraction
    for string in lst: 
        result = re.search(r'(\D+)(\d+\w+)', string)
        if result:
            back = result.group(0)
            match = re.match(r"([A-Za-z\s]+)(\d+.*)", back)
            if match != None:
                front = match.group(1).strip()
                back = match.group(2).strip()

                # Record data
                with open(outputfile, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([front, back, record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7].replace("%20", " ")])
input("Completed")