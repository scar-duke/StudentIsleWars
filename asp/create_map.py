from embasp.platforms.desktop.desktop_handler import DesktopHandler
from embasp.specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService
from embasp.specializations.dlv.dlv_filter_option import DLVFilterOption
from embasp.languages.asp.asp_input_program import ASPInputProgram

def add_dlv_program(handler, program_file_name):
    input = ASPInputProgram()
    program = ""

    with open(program_file_name) as file:
        for line in file:
            if (not(("%" in line) or ("#show" in line))):
                program += line
    input.add_program(program)
    return handler.add_program(input)


def create_map_from_dlv(file_name, cleaned):
    ## cleaned[0] is territories, cleaned[1] is neighbors, cleaned[2] is continent assignments
    # create json file name and path for saving/creating
    json_file = file_name.split("/")[3].split(".")[0] + ".json"
    json_file = "./data/" + json_file

    # write file with proper json formatting
    with open(json_file, "w") as file:
        file.write('{"territories":[\n')
        sz = len(cleaned[0])
        neighbors = cleaned[1]
        continents = cleaned[2]

        for i in range(sz):
            file.write('{"name":"'+str(cleaned[0][i])+'","owner_id": -1, "continent_id":'+str(continents[cleaned[0][i]])+', "armies": 0,"neighbors":'+ str(neighbors[cleaned[0][i]]).replace("'","\"")+'}')
            if i != sz-1:
                file.write(",")
            file.write("\n")
        file.write(']}')


def parse_map_dlv(file_name):
    handler = DesktopHandler(DLV2DesktopService("./asp/executable/dlv-2.1.2-win64.exe"))
    try:
        options = DLVFilterOption("");
        options.clear() # clearing is required bc the default options are set up wrong
        options.add_option("--filter=neighbor/2,connected/2,territory/1,assigned/2")
        handler.add_option(options)

        add_dlv_program(handler, file_name)

        answer_sets = handler.start_sync()

        for answer_set in answer_sets.get_answer_sets():
            answer = str(answer_set).replace("[","").replace("]","").replace("'","").split(", ")
            territories = []
            neighbors = {}
            assigned = {}

            # clean answer set for map creation
            for item in answer:
                #print(item)
                if "territory" in item:
                    territories.append(item[10:].split(")")[0])
                if "neighbor" in item or "connected" in item:
                    d = item.split("(")[1].split(")")[0].split(",")
                    if d[0] not in neighbors:
                        neighbors[d[0]] = []
                    neighbors[d[0]].append(d[1])
                if "assigned" in item:
                    d = item.split("(")[1].split(")")[0].split(",")
                    assigned[d[0]] = d[1]
            
            create_map_from_dlv(file_name, [territories, neighbors, assigned])

    except Exception as e:
        print(str(e))

parse_map_dlv("./asp/programs/default_map.dlv")