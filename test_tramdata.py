import unittest
from tramdata import *

TRAM_FILE = './tramnetwork.json'

class TestTramData(unittest.TestCase):

    def setUp(self):
        with open(TRAM_FILE) as trams:
            tramdict = json.loads(trams.read())
            self.stopdict = tramdict['stops']
            self.linedict = tramdict['lines']
            self.timedict = tramdict["times"]

    def test_stops_exist(self):
        stopset = {stop for line in self.linedict for stop in self.linedict[line]}
        for stop in stopset:
            self.assertIn(stop, self.stopdict, msg = stop + ' not in stopdict')

    # add your own tests here
    def test_lines_exist(self):
        
        expected_lines = {str(x) for x in range(1, 14) if x != 12}
        actual_lines = set(self.linedict.keys())

        for line in expected_lines:
            self.assertIn(line, actual_lines, msg=f"Line {line} not in linedict")

    def test_stops_same(self):
        with open("tramlines.txt") as f:
            tramlines = {}
            current_line = None

            for line in f:
                line = line.strip()
                if not line:
                    continue
            
                if ':' in line:
                    current_line = line.split(':')[0].strip()
                elif current_line:
                    stop_name = ' '.join(line.split()[:-1]).strip()
                    if stop_name:
                        if current_line not in tramlines:
                            tramlines[current_line] = []
                        tramlines[current_line].append(stop_name)


        for line, stops in tramlines.items():
            self.assertIn(line, self.linedict, msg=f"Line {line} not found in linedict")
            expected_stops = self.linedict[line]
            self.assertEqual(stops, expected_stops, msg=f"Stops for line {line} do not match")


    def test_feasible_distance(self):
        for stop1 in self.stopdict:
            coord1 = (self.stopdict[stop1]['lat'], self.stopdict[stop1]['lon'])

            for stop2 in self.stopdict:
                if stop1 == stop2:
                    continue
            
                coord2 = (self.stopdict[stop2]['lat'], self.stopdict[stop2]['lon'])
                distance = haversine(coord1, coord2)

                self.assertLessEqual(distance, 20, msg = f"Aware: Distance between {stop1} and {stop2} is over 20km")

    def test_same_time(self):
        for stop1 in self.timedict:
            for stop2 in self.timedict[stop1]:
                s1_s2 = self.timedict[stop1].get(stop2)
                s2_s1 = self.timedict.get(stop2, {}).get(stop1)


                if s1_s2 is not None or s2_s1 is not None:
                    continue
                self.assertEqual(
                        s1_s2, 
                        s2_s1, 
                        msg=f"Time between {stop1} and {stop2} does not match: {s1_s2} vs {s2_s1}")


if __name__ == '__main__':
    unittest.main()