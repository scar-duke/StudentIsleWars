from embasp.platforms.desktop.desktop_handler import DesktopHandler
from embasp.specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService
from embasp.specializations.dlv.dlv_filter_option import DLVFilterOption
from embasp.languages.asp.asp_input_program import ASPInputProgram
from asp.create_map import add_dlv_program
from game.models import Territory

def add_dlv(handler, info: list):
    input = ASPInputProgram()
    program = ""

    for item in info:
        program += item
    input.add_program(program)
    return handler.add_program(input)

def call_dlv_handler(agent_file: str, info: list, filter: str):
    handler = DesktopHandler(DLV2DesktopService("./asp/executable/dlv-2.1.2-win64.exe"))
    try:
        options = DLVFilterOption("");
        options.clear() # clearing is required bc the default options are set up wrong
        options.add_option(filter)
        handler.add_option(options)

        add_dlv(handler, info)
        add_dlv_program(handler, "./asp/programs/world.dlv")
        add_dlv_program(handler, agent_file)

        answer_sets = handler.start_sync()

        # get last generated answer set (one of the optimals)
        answer_set = answer_sets.get_answer_sets()[-1]
        answer = str(answer_set).replace("[","").replace("]","").replace("'","").split(", ")
        #print(answer)
        return answer

    except Exception as e:
        print(str(e))
        return "ERROR"
            

def create_world_information(territories: list[Territory]):
    info = []
    for territory in territories:
        info.append("territory("+str(territory.name)+").")
        info.append("in_continent("+str(territory.name)+","+str(territory.continent_id)+").")
        #info.append("armies_present("+str(territory.name)+","+str(territory.armies)+").")
        #info.append("owner("+str(territory.name)+","+str(territory.owner_id)+").")
        neighs = []
        for neig in territory.neighbors:
            neighs.append("neighbor("+str(territory.name)+","+str(neig)+").")
        info += neighs
    info.sort()
    with open("./asp/programs/world.dlv", "w", encoding="utf-8") as file:
        for i in info:
            file.write(i + "\n")
    return info

def update_world_information(id: int, phase: str, territories: list[Territory], extra: str):
    info = [extra]
    info.append("my_id("+str(id)+").")
    info.append("phase("+phase+").")
    for territory in territories:
        info.append("armies_present("+str(territory.name)+","+str(territory.armies)+").")
        info.append("owner("+str(territory.name)+","+str(territory.owner_id)+").")
    info.sort()
    with open("./asp/programs/agent_"+str(id)+"_info.dlv", "w", encoding="utf-8") as file:
        for i in info:
            file.write(i + "\n")
    return info
    