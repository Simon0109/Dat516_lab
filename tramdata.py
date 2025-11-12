import json
import sys
from haversine import haversine, Unit

def build_tram_stops(jsonobject):
    with open(jsonobject, 'r') as f:
        data = json.load(f)
        stops = {
            key: {
                "lat": float(pos["position"][0]),
                "lon": float(pos["position"][1])
    }
    for key, pos in data.items()
    }
    
    return stops

def build_tram_lines(lines):
    l_dict = {}
    t_dict = {}

    with open(lines, 'r') as f:
        current_t = None
        prev_s_name = None
        prev_s_time = None
        prev_t = None

        for l in f:
            l = l.strip()

            if l.endswith(':'):
                current_t = l[:-1]
                l_dict[current_t] = []
            elif l:
                s_name = ' '.join(l.split()[:-1])
                s_time = l.split()[-1]

                if s_name not in l_dict[current_t]:
                    l_dict[current_t].append(s_name)

                    if prev_s_time is not None:
                        if current_t == prev_t:
                            prev_time_parts = list(map(int, prev_s_time.split(':')))
                            current_time_parts = list(map(int, s_time.split(':')))
                        
                            prev_minutes = prev_time_parts[0] * 60 + prev_time_parts[1]
                            current_minutes = current_time_parts[0] * 60 + current_time_parts[1]

                            t_between = abs(current_minutes - prev_minutes)

                            if prev_s_name not in t_dict:
                                t_dict[prev_s_name] = {}

                            if s_name not in t_dict[prev_s_name]:
                                t_dict[prev_s_name][s_name] = t_between
                    
                    prev_s_name = s_name
                    prev_s_time = s_time
                    prev_t = current_t

    return l_dict, t_dict


def build_tram_network(stopfile, linefile):

    stops = build_tram_stops(stopfile)
    

    lines, times = build_tram_lines(linefile)
    

    tram_network = {
        "stops": stops,
        "lines": lines,
        "times": times
    }
    
    with open("tramnetwork.json", "w") as json_f:
        json.dump(tram_network, json_f, ensure_ascii=False, indent=4)


def lines_via_stop(linedict, stop):
    lines = sorted([line for line, stops in linedict.items() if stop in stops], key=int)
    return lines


def lines_between_stops(linedict, stop1, stop2):
    return sorted([line for line, stops in linedict.items() if stop1 in stops and stop2 in stops], key=int)


def time_between_stops(linedict, timedict, line, stop1, stop2):

    if line not in linedict:
        return "Error! Line not found"
    
    stops = linedict[line]
    
    if stop1 not in stops or stop2 not in stops:
        return "Error! The stops are not along the same line"
    
    index1, index2 = stops.index(stop1), stops.index(stop2)

    if index1 > index2:
        index1, index2 = index2, index1

    total_time = 0

    for i in range(index1, index2):
        total_time += timedict[stops[i]][stops[i+1]]
    return total_time


def distance_between_stops(stopdict, stop1, stop2):
    if stop1 not in stopdict or stop2 not in stopdict:
        return "Stop is not available"
    
    coord1 = (stopdict[stop1]["lat"], stopdict[stop1]["lon"])
    coord2 = (stopdict[stop2]["lat"], stopdict[stop2]["lon"])

    return haversine(coord1, coord2, Unit.KILOMETERS)


def answer_query(tramdict, query):
    ans = query.split()

    linedict = tramdict["lines"]
    timedict = tramdict["times"]
    stopdict = tramdict["stops"]
    
    if ans[0] == "via":
        if len(ans) == 2:
            if ans[1] in stopdict:
                return lines_via_stop(linedict, ans[1])
            else:
                return "unknown arguments"
        elif len(ans) == 3:
            stop = " ".join(ans[1:3])
            if stop in stopdict:
                return lines_via_stop(linedict, stop)
            else:
                return "unknown arguments"
    
    elif ans[0] == "between":
        stop1 = " ".join(ans[1:ans.index("and")]).strip(",")
        stop2 = " ".join(ans[ans.index("and") + 1:]).strip(",")
        if stop1 in stopdict and stop2 in stopdict:
            return lines_between_stops(linedict, stop1, stop2)
        else:
            return "unknown arguments"

    
    elif ans[0] == "time" and ans[1] == "with":
        if len(ans) >= 5 and "from" in ans and "to" in ans:
            line = ans[2].strip() 
            stop1 = ' '.join(ans[4:ans.index('to')]).strip()  
            stop2 = ' '.join(ans[ans.index('to') + 1:]).strip()
            if line in linedict and stop1 in stopdict and stop2 in stopdict:
                return time_between_stops(linedict, timedict, line, stop1, stop2)
            else:
                return "unknown arguments"
    

    elif ans[0] == "distance":
        stop1 = " ".join(ans[2:ans.index("to")]).strip(",")
        stop2 = " ".join(ans[ans.index("to") + 1:]).strip(",")
        if stop1 in stopdict and stop2 in stopdict:
            return distance_between_stops(stopdict, stop1, stop2)
        else:
            return "unknown arguments"
    return "sorry, try again"


def dialogue(tramfile):
    with open(tramfile, "r") as f:
        tramdict = json.load(f)

    while True:
        q = input("> ")

        if q.lower() == "quit":
            print("Exiting the dialogue.")
            break
        
        result = answer_query(tramdict, q)
        
        if result is False or result == "sorry, try again":
            print(result)
        else:
            print(result)


if __name__ == '__main__':
    if sys.argv[1:] == ['init']:
        build_tram_network("tramlines.txt", "tramstops.json")
    else:
        dialogue("tramnetwork.json")