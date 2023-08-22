import csv, sys, re
from tabulate import tabulate

GDPindexes = []
# elasticity index
EI = {"t": 0.35, "tt": 1.00, "b": 1.00}
# conversion indexes to standard 100kN axle
R = {
    "truck": {"highway": {"115kN": 0.50},
          "state road": {"115kN": 0.50},
          "regional road": {"115kN": 0.45, "100kN": 0.45},
          },
    "truck + trailer": {"highway": {"115kN": 1.95},
          "state road": {"115kN": 1.80},
          "regional road": {"115kN": 1.70, "100kN": 1.60},
          },
    "bus": {"highway": {"115kN": 1.25},
          "state road": {"115kN": 1.20},
          "regional road": {"115kN": 1.15, "100kN": 1.05},
          },
    }
# factor related with number of lanes, direction
F1 = {
    "1": {"twoway": 1.00, "oneway": 1.00},
    "2": {"twoway": 0.50, "oneway": 0.90},
    "3": {"twoway": 0.50, "oneway": 0.70},
    "4": {"twoway": 0.45, "oneway": 0.70},
    "5": {"twoway": 0.45, "oneway": 0.70},
    "6+": {"twoway": 0.35, "oneway": 0.70},
    }
# line width factor
F2 = {
    "s>=3.50m": 1.00,
    "3.00m<=s<3.50m": 1.06,
    "2.75m<=s<3.00m": 1.13,
    "s<2.75m": 1.25,
    }
# road slope factor
F3 = {
    "i<6%": 1.00,
    "6%<=i<7%": 1.10,
    "7%<=i<9%": 1.25,
    "9%<=i<10%": 1.35,
    "i>=10%": 1.45,
    }


def main():
    # load gdp indexes form csv file
    initiate_GDPindexes()

    # ask user what to do if command is not recognized help hit will show
    while True:
        c = input("command: ").lower()
        match c:
            case "region" | "r":
                region()
            case "quit" | "q":
                sys.exit()
            case "help" | "h":
                help()
            case "start" | "s":
                break
            case _:
                help()

    # take input basic data and make sure numbers are integers
    while True:
        try:
            trucks = int(input("Average number of trucks without trailers a day: "))
            trucks_trailers = int(input("Average number of trucks with trailers a day: "))
            buses = int(input("Average number of buses a day: "))
        except ValueError:
            print("\n== !! == It is not an integer!\n")
            continue
        else:
            break

    # take input for design life
    while True:
        try:
            years = get_years(input("Design life of road. (year-year): "))
            break
        except ValueError as e:
            print(e)
            continue

    # take input for region id
    while True:
        try:
            reg = region(input("region id: "))
        except ValueError as e:
            print(e)
            continue
        else:
            if reg is None:
                continue
            else:
                break

    # take input for type of road
    while True:
        try:
            road = set_road()
            break
        except ValueError as e:
            print(e)
            continue

    # take input for designed load for axle
    while True:
        try:
            axle = set_axle(road)
            break
        except ValueError as e:
            print(e)
            continue

    # take input for factor dependent on number of lanes
    while True:
        try:
            f1 = set_f1()
            break
        except ValueError as e:
            print(e)
            continue

    # take input for factor dependent on width of lanes
    while True:
        try:
            f2 = set_f2()
            break
        except ValueError:
            print("\n== !! == Invalid input, width should be positive floating point number.")
            continue

    # take input for factor dependent on slope of the road
    while True:
        try:
            f3 = set_f3()
            break
        except ValueError:
            print("\n== !! == Invalid input, slope should be positive floating point number.\n")
            continue

    # compute accumulated road tragic indexes
    acum_ri = accumulated_ri(years, reg)

    # compute total number of vehicle in design life
    nt = total(trucks, acum_ri["trucks"])
    ntt = total(trucks_trailers, acum_ri["trucks_trailers"])
    nb = total(buses, acum_ri["buses"])

    # conversion indexes
    rt, rtt, rb = set_r(road, axle)

    # calculate number of standard 100kN axles
    n100 = f1 * f2 *f3 * (nt * rt + ntt * rtt + nb * rb)
    n100 = round(n100)
    millions_of_n100 = n100 / 1000000

    # assign traffic category and printing output of program
    traffic_category = category(millions_of_n100)
    print(f"\n\nN100: {millions_of_n100:.2f} mln of 100kN axles\nTraffic Category: {traffic_category}")


def initiate_GDPindexes():
    # csv file prepared by excractor.py
    # populate GDPindexes list
    with open("GDP growth index - clean.csv") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            GDPindexes.append(row)

# default variable is used for testing
def set_road(n=None):
    if n is None:
        print("\nSelect type of road. Enter related number.\n1. highway \n2. state road \n3. regional road\n")
        n = input("Select a number: ")
    if n in ["1", "2", "3"]:
        match n:
            case "1":
                return "highway"
            case "2":
                return "state road"
            case "3":
                return "regional road"
    else:
        raise ValueError("== !! == Invalid input, enter 1, 2 or 3")


# default n variable is used for testing
def set_axle(road, n=None):
    # for highway and state road function omit choosing design axle load
    if road == "regional road":
        if n is None:
            print("\nSelect designed axle load. Enter related number.\n1. 115kN \n2. 100kN\n")
            n = input("Select a number: ")
        if n in ["1", "2"]:
            match n:
                case "1":
                    return "115kN"
                case "2":
                    return "100kN"
        else:
            raise ValueError("== !! == Invalid input, enter 1 or 2")
    elif road in ["highway", "state road"]:
        return "115kN"
    else:
        raise ValueError("Invalid road name")



def set_r(road, axle):
    global R
    # two if statement used main for testing
    if road == "highway" and axle == "100kN":
        raise KeyError("highway designed axle load is 115kN not 100kN!")
    if road == "state road" and axle == "100kN":
        raise KeyError("state road designed axle load is 115kN not 100kN!")

    # read proper conversion indexes from global R dictionary
    rt = R["truck"][road][axle]
    rtt = R["truck + trailer"][road][axle]
    rb = R["bus"][road][axle]
    return rt, rtt, rb


# default n variable is used for testing
def set_f1(d=None, w=None):
    global F1
    # take input from user. Test script omits input()
    if d is None:
        d = input("\nNumber of lanes. If there is more then 6 please enter 6+\n\nSelect a number: ")

    if w is None:
        print("\nIs road: \n1. oneway \n2. twoway\n")
        w = input("Select a number: ")

    # Validation of input
    if not d in ["1", "2", "3", "4", "5", "6+"] or not w in ["1", "2"]:
        raise ValueError("""
== !! == Enter from 1 to 5 or 6+ for numbers of lanes.
== !! == Enter 1 or 2 for direction""")

    # return f1 factor from global dict
    if w == "1":
        return F1[d]["oneway"]
    elif w == "2":
        return F1[d]["twoway"]


# default n variable is used for testing
def set_f2(s=None):
    global F2
    # allow to omit while testing
    if s is None:
        s = float(input("\nWidth of lanes [m]: "))

    if s >= 3.50:
        return F2["s>=3.50m"]
    elif  3.00 <= s < 3.50:
        return F2["3.00m<=s<3.50m"]
    elif  2.75 <= s < 3.00:
        return F2["2.75m<=s<3.00m"]
    elif 0 < s < 2.75:
        return F2["s<2.75m"]
    elif s <= 0:
        raise ValueError


# default n variable is used for testing
def set_f3(s=None):
    # allow to omit while testing
    if s is None:
        s = float(input("Slope of road [%]: "))

    global F3
    if s >= 10:
        return F3["i>=10%"]
    elif  9 <= s < 10:
        return F3["9%<=i<10%"]
    elif  7 <= s < 9:
        return F3["7%<=i<9%"]
    elif 6 <= s < 7:
        return F3["6%<=i<7%"]
    elif 0 < s < 6:
        return F3["i<6%"]
    elif s <= 0:
        raise ValueError


def get_years(y):
    # validate input of design life of road
    if _ := re.search(r"^20[1-9]\d-20[1-9]\d$", y):
        s, e = y.split("-")
        if int(s) > int(e):
            raise ValueError("\n== !! == start year must not be lower then end year!\n")
        else:
            return {"start": s, "end": e}
    else:
        raise ValueError("\n== !! == Invalid date format! Enter date like yyyy-yyyy in period of time from 2020 to 2060\n")


# default n variable is used for testing
def region(id=None):
    region_list = []
    global GDPindexes
    for i in GDPindexes[1:]:
        region_list.append([i[0], i[1]])

    if id in ["r", "region"]:
        region()
    elif id:
        try:
            id = int(id)
        except:
            raise ValueError("""
== !! == id must be an integer
== !! == If you don't know region id use command 'region' or 'r'
""")

    if id in range(1,len(region_list)):
        return int(region_list[id-1][0])
    elif id is None:
        # print table of regions with GDP indesx
        headers = ["id", "name"]
        print(tabulate(region_list, headers, tablefmt="grid"))
    else:
        raise ValueError(f"""
== !! == id out of range, enter id in range from 1 to {len(region_list)}
== !! == If you don't know region id use command 'region' or 'r'
""")


def accumulated_ri(year, reg):
    global GDPindexes
    global EI
    start = GDPindexes[0].index(year["start"])
    end = GDPindexes[0].index(year["end"])
    reg_indexes = GDPindexes[reg]
    # list of accumulated road traffic indexes for each year in design life of road for trucks, trucks with trailers, buses.
    acum_ri_t = []
    acum_ri_tt = []
    acum_ri_b = []
    for i in range(start, end + 1):
        road_index_t = EI["t"] * float(reg_indexes[i]) / 100 + 1
        road_index_tt = EI["tt"] * float(reg_indexes[i]) / 100 + 1
        road_index_b = EI["b"] * float(reg_indexes[i]) / 100 + 1
        if i == start:
            acum_ri_t.append(round(road_index_t, ndigits=4))
            acum_ri_tt.append(round(road_index_tt, ndigits=4))
            acum_ri_b.append(round(road_index_b, ndigits=4))
        else:
            acum_ri_t.append(round(acum_ri_t[i - start - 1] * road_index_t, ndigits=4))
            acum_ri_tt.append(round(acum_ri_tt[i - start - 1] * road_index_tt, ndigits=4))
            acum_ri_b.append(round(acum_ri_b[i - start - 1] * road_index_b, ndigits=4))
    return {"trucks": acum_ri_t, "trucks_trailers": acum_ri_tt, "buses": acum_ri_b}


def total(vehicle, road_indexes):
    sum_vehicle = 0
    for i in range(len(road_indexes)):
        sum_vehicle += vehicle * road_indexes[i]
    sum_vehicle = round(sum_vehicle * 365)
    return sum_vehicle


def category(n100):
    n100 = round(n100, 2)
    if n100 <= 0.03:
        return "None - road traffic is too small to assign"
    elif 0.03 < n100 <= 0.09:
        return "KR1"
    elif 0.09 < n100 <= 0.50:
        return "KR2"
    elif 0.50 < n100 <= 2.50:
        return "KR3"
    elif 2.50 < n100 <= 7.30:
        return "KR4"
    elif 7.30 < n100 <= 22.00:
        return "KR5"
    elif 22.00 < n100 <= 52.00:
        return "KR6"
    elif n100 > 52.00:
        return "KR7"


def help():
    print("""
    Enter:
    1. start or s - start process of computing road traffic category
    2. region or r - show table of regions, id from that table is necessary for calculation
    3. quit or q - quit a program
    4. help or h - help
    """)


if __name__ == "__main__":
    main()