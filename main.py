'''Project BusRider'''

import re
import json
import itertools

class BusRider:
    stop_type = ['S', 'O', 'F', '']
    total_errors = 0
    basic_data = {
        "bus_id": {"type": int, "required": True, },
        "stop_id": {"type": int, "required": True},
        "stop_name": {"type": str, "required": True,
                      "format": re.compile(r'^[A-Z].+ (Road|Avenue|Boulevard|Street)$')},
        "next_stop": {"type": int, "required": True},
        "stop_type": {"type": "char", "required": False, "format": re.compile(r'^[SOF]?$')},
        "a_time": {"type": str, "required": True, "format": re.compile(r'^([01]\d|2[0-3]){1}:([0-5]\d){1}$')}
    }
    count_dict_format = {"stop_name": 0, "stop_type": 0, "a_time": 0}
    total_format_errors = 0

    def __init__(self, text):
        with open("input_data.json", "w") as json_file:
            json_file.write(text)
            # json input deserialization
        with open("input_data.json", "r") as json_file:
            json_dict = json.load(json_file)
        self.text = json_dict

    def error_count(self):
        count_dict = {}
        for x in self.basic_data:
            count_dict[x] = self.basic_data[x]
        for x in self.basic_data.keys():
            count_dict[x] = 0
        # count errors
        for x in list(self.basic_data.keys()):
            for y in range(len(self.text)):
                if x != 'stop_type' and (self.basic_data[x]["type"] != type(self.text[y][x]) or self.text[y][x] == ''):
                    self.total_errors += 1
                    count_dict[x] += 1
                elif x == 'stop_type' and self.text[y][x] not in self.stop_type:
                    self.total_errors += 1
                    count_dict[x] += 1
        print(f'Type and required field validation: {self.total_errors} errors')
        for x in count_dict:
            print(str(x) + ': ' + str(count_dict[x]))

    def format_error_count(self):
        for part in self.text:
            for key in list(self.count_dict_format.keys()):
                if not re.match(self.basic_data[key]["format"], part[key]):
                    self.count_dict_format[key] += 1
                    self.total_format_errors += 1
        # print output
        print(f'Format validation: {self.total_format_errors} errors')
        for x in self.count_dict_format:
            print(str(x) + ': ' + str(self.count_dict_format[x]))

    def lines_and_stops_count(self):
        lines_and_stops = {}
        for x in self.text:
            lines_and_stops.update({str(x["bus_id"]): []})
        for x in self.text:
            key = str(x["bus_id"])
            item_for_list = str(x["stop_id"])
            if item_for_list not in lines_and_stops[key]:
                lines_and_stops[key].append(item_for_list)
        for x in lines_and_stops:
            print(f'bus_id: {x}, stops: {len(lines_and_stops[x])}')

    def stops_checker(self):
        bus_ids = {}
        supp_param = 1
        start_stops = []
        final_stops = []
        trans_stops = []
        for x in self.text:
            bus_ids.update({str(x["bus_id"]): {'S': [], 'F': [], 'O': []}})
        for y in self.text:
            for x in bus_ids:
                if str(y["bus_id"]) == x:
                    if str(y["stop_type"]) != 'S' and str(y["stop_type"]) != 'F':
                        bus_ids[x]['O'].append(y["stop_name"])
                    else:
                        bus_ids[x].update({str(y["stop_type"]): [y["stop_name"]]})
        for x in bus_ids:
            if not bus_ids[x]['S'] or not bus_ids[x]['F']:
                print(f'There is no start or end stop for the line: {x}')
                supp_param = 0
                break
        if supp_param:
            for x in bus_ids:
                for y in bus_ids[x]:
                    if y == 'S':
                        start_stops += bus_ids[x][y]
                    if y == 'F':
                        final_stops += bus_ids[x][y]
                    if True:
                        trans_stops += bus_ids[x][y]
            trans_dict = {}.fromkeys(trans_stops, 0)
            for i in trans_stops:
                trans_dict[i] += 1
            trans_stops_1 = []
            for x in trans_dict:
                if trans_dict[x] > 1:
                    trans_stops_1.append(x)
            print(f'Start stops: {len(sorted(list(set(start_stops))))} {sorted(list(set(start_stops)))}')
            print(f'Transfer stops: {len(sorted(list(set(trans_stops_1))))} {sorted(list(set(trans_stops_1)))}')
            print(f'Finish stops: {len(sorted(list(set(final_stops))))} {sorted(list(set(final_stops)))}')

    def transfer_time_checker(self):
        bus_ids = {}
        bus_ids_checklist = {}
        counter_checker = 0
        final_list = []
        for x in self.text:
            bus_ids.update({str(x["bus_id"]): []})
            bus_ids_checklist.update({str(x["bus_id"]): []})
        for y in self.text:
            bus_ids[str(y["bus_id"])].append(y["stop_name"])
            bus_ids[str(y["bus_id"])].append(y["a_time"])
        for x in bus_ids:
            for y in range(1, len(bus_ids[x]) - 2, 2):
                if not bus_ids_checklist[x] and bus_ids[x][y + 2] <= bus_ids[x][y]:
                    bus_ids_checklist[x].append(bus_ids[x][y + 1])
                    counter_checker += 1
        if counter_checker > 0:
            for x in bus_ids_checklist:
                if bus_ids_checklist[x]:
                    final_list.append(f'bus_id line {x}: wrong time on station {bus_ids_checklist[x][0]}')
            print('Arrival time test:')
            for x in final_list:
                print(x)
        else:
            print('Arrival time test:' + '\n' + 'OK')

    def stop_type_checker(self):
        wrong_stops = []
        s_and_f = ['Sesame Street', 'Sunset Boulevard', 'Bourbon Street', 'Pilotow Street', 'Prospekt Avenue', 'Elm Street']
        for i in self.text:
            if i["stop_type"] not in ['S', 'F', ''] and i["stop_name"] in s_and_f:
                wrong_stops.append(i["stop_name"])
        wrong_stops_x = [i for i, _ in itertools.groupby(wrong_stops)]
        print('On demand stops test:')
        if wrong_stops_x:
            print(f'Wrong stop type: {wrong_stops_x}')
        else:
            print('OK')


if __name__ == '__main__':
    bus_1 = BusRider(input())
    BusRider.error_count(bus_1)
    BusRider.format_error_count(bus_1)
    BusRider.lines_and_stops_count(bus_1)
    BusRider.stops_checker(bus_1)
    BusRider.transfer_time_checker(bus_1)
    BusRider.stop_type_checker(bus_1)





