import csv, json

# number of extra years to extend official table by copying last column multiple time
extra = 0
try:
    extra = int(input("indexes are published up to 2040. How many years do you want to add: "))
except ValueError:
    pass

# file with raw data copied from pdf and paste to txt
infile = "GDP growth index - raw copy-paste.txt"
file = open(infile)
# number of rows with needless data
start_row = 4
# number of rows for each item/region to extract
cycle = 38

# create new csv file with sorted data
with open("GDP growth index - clean.csv", "w") as csvfile:
    tmp_line = ""
    cycle_count = 0
    # converting txt file with one value on row to csv table like in original PDF file with out needless data
    for i, line in enumerate(file):
        # omit a few firs raw
        if i < start_row:
            continue
        # omitting row with main region names only subreginos matter
        if line.strip().endswith("OM"):
            continue
        # after * there are needles data - end of iteration
        if line.startswith("*"):
            csvfile.write(tmp_line.rstrip(","))
            break

        # translation polish characters to latin
        if (
        line.find("\u0142") != -1 or
        line.find("\u00f3") != -1 or
        line.find("\u017a") != -1 or
        line.find("\u0119") != -1 or
        line.find("\u015b") != -1 or
        line.find("\u0105") != -1):
            trans = {
                0x00f3: 111,
                0x141: 76,
                0x0142: 108,
                0x0144: 110,
                0x017a: 122,
                0x0119: 101,
                0x015b: 115,
                0x0105: 97,
                0x017c: 122,
            }
            line = line.translate(trans)

        # extending temporary line
        tmp_line = tmp_line + line.strip().replace(",", ".") + ","
        cycle_count += 1

        # saving temporary line in new csv file for each item/region
        if cycle_count % cycle == 0:
            csvfile.write(tmp_line.rstrip(",") + "\n")
            # reset temporary variables
            cycle_count = 0
            tmp_line = ""
file.close()

# list of key for json file
fieldnames = []
# temporary variable used to rearrange data
indexes = []
# delete unused columns from csv file
with open("GDP growth index - clean.csv") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        indexes.append(row)

    for i, item in enumerate(indexes):
        if item[0] != "POLSKA*":
            item.pop(4)
            item.pop(3)
            item.pop(2)
        else:
            item.insert(0, i)

    fieldnames = indexes[0]

    # adding additional years
    if extra != 0:
        new_indexes = []
        new_years = []
        last_year = int(indexes[0][-1:][0])
        last_indexes = []
        # indexes for year 2040
        for i in range(0, len(indexes)):
            last_indexes.append([indexes[i][-1:][0]])
        # generate extra years
        for i in range(extra):
            indexes[0].append(str(last_year + i + 1))
        # appendind extra times indexes for each region
        for i in range(1, len(indexes)):
            for _ in range(extra):
                indexes[i].append(last_indexes[i][0])

# write converted data to csv file
with open("GDP growth index - clean.csv", "w") as csvfile:
    writer = csv.writer(csvfile)
    for item in indexes:
        writer.writerow(item)

# additional json file containing the same data as csv file.
json_dict = {}
with open("GDP growth index - clean.csv") as csvfile:
    with open("GDP growth index - clean.json", "w") as jfile:
        for row in indexes[1:]:
            tmp = {}
            for i in range(1,len(row)):
                tmp[fieldnames[i]] = row[i]

            json_dict[row[0]] = tmp
        js = json.dumps(json_dict, indent=4)
        jfile.write(js)
