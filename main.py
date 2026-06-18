'''
Put your DLV file into the asp/programs folder and replace the YOUR_FILE_NAME_HERE with the name
    of your code file.
    
By default, you are set up against two very dumb random computer players. If you want to play against
    players of the same thought process as your own bot, comment out the RandomComputerPlayers then
    uncomment and fix the two BasicASPPlayers to have the same file path as your Player 0
'''

import time
from game.engine import GameEngine
from game.setup import create_initial_state_from_file
from players.basic_asp_player import BasicASPPlayer
from players.computer_random import RandomComputerPlayer
from players.human_text import HumanTextPlayer
from ui.text_view import print_action_result, print_board, print_game_over

max_armies = 6
add_delay = True

your_dlv_file = "./asp/programs/YOUR_FILE_NAME_HERE.dlv"

def createControllers():
    return {
        #0: HumanTextPlayer(0, "Human"),
        0: BasicASPPlayer(0, "My Team", your_dlv_file),
        
        ### Random Computer Players
        1: RandomComputerPlayer(1, "Computer 1"),
        2: RandomComputerPlayer(2, "Computer 2"),
        
        ### ASP players if you want to have three of your own bots against each other
        #1: BasicASPPlayer(1, "DLV Player 1", your_dlv_file),
        #2: BasicASPPlayer(2, "DLV Player 2", your_dlv_file),
    }


def runGame():
    controllers = createControllers()
    state = create_initial_state_from_file(controllers, "data/default_map.json", max_armies)
    engine = GameEngine(state)

    while not engine.is_game_over():
        print_board(engine.state)
        player_id = engine.state.current_player_id
        controller = controllers[player_id]
        action = controller.choose_action(engine.state)
        result = engine.apply_action(action)
        print_action_result(result)
        
        if add_delay:
            time.sleep(2)

    print_board(engine.state)
    print_game_over(engine.state)


def main():
    runGame()


if __name__ == "__main__":
    main()
