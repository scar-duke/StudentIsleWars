import time
import pygame
from game.engine import GameEngine
from game.setup import create_initial_state_from_file
from players.basic_asp_player import BasicASPPlayer
from players.computer_random import RandomComputerPlayer
from players.human_text import HumanTextPlayer
from ui.renderer import (
    build_territory_templates,
    draw_board_state,
    load_map_data,
)
from ui.text_view import print_action_result, print_board, print_game_over

MAP_PATH = "./data/full_map.json"
max_armies = 6
add_delay = True
scale = 0.6

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

    turn_over = False

    pygame.init()

    map_data = load_map_data(MAP_PATH)

    board_path = "./assets/islewars_modified.jpg"
    mask_path = "./assets/full_mask.png"
    width = int(1920 * scale)
    height = int(1080 * scale)

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("DLV Isle Wars")

    board_surface = pygame.image.load(board_path).convert()
    board_surface = pygame.transform.scale(board_surface, (width, height))
    mask_surface = pygame.image.load(mask_path).convert_alpha()
    mask_surface = pygame.transform.scale(mask_surface, (width, height))

    templates = build_territory_templates(
        mask_surface,
        map_data["territories"]
    )

    font = pygame.font.SysFont(None, 26)

    controllers = createControllers()
    state = create_initial_state_from_file(controllers, "data/full_map.json", max_armies)
    engine = GameEngine(state)
    draw_board_state(screen, board_surface, templates, state.territories, font, scale)
    pygame.display.flip()

    ### =========================================== Start Actual Game
    while not engine.is_game_over():
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

        #print_board(engine.state)
        player_id = engine.state.current_player_id
        controller = controllers[player_id]
        action = controller.choose_action(engine.state)
        result = engine.apply_action(action)
        print_action_result(result)
        if str(action) == "EndPhaseAction()":
             turn_over = True
       
        if turn_over:
            turn_over = False
            draw_board_state(screen, board_surface, templates, state.territories, font, scale)
            pygame.display.flip()


    print_board(engine.state)
    print_game_over(engine.state)
    draw_board_state(screen, board_surface, templates, state.territories, font, scale)
    pygame.display.flip()

    # show final board state for a few seconds before terminating program
    time.sleep(3)
    pygame.quit()


def main():
    runGame()


if __name__ == "__main__":
    main()
