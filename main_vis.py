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
show_vis = True
scale = 0.6

def createControllers():
    return {
        #0: HumanTextPlayer(0, "Human"),
        #1: RandomComputerPlayer(1, "Computer 1"),
        #2: RandomComputerPlayer(2, "Computer 2"),
        0: BasicASPPlayer(0, "DLV Player 0", "./asp/programs/new_bot.dlv"),
        1: BasicASPPlayer(1, "DLV Player 1", "./asp/programs/students/team2.dlv"),
        2: BasicASPPlayer(2, "DLV Player 2", "./asp/programs/students/team3.dlv"),
        3: BasicASPPlayer(3, "DLV Player 3", "./asp/programs/students/team4.dlv"),
        4: BasicASPPlayer(4, "DLV Player 4", "./asp/programs/students/team5.dlv"),
        5: BasicASPPlayer(5, "DLV Player 5", "./asp/programs/students/team6.dlv"),
    }

def run_w_vis(controllers, state, engine):
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

    time.sleep(4)
    pygame.quit()

def runGame():
    controllers = createControllers()
    state = create_initial_state_from_file(controllers, "data/full_map.json", max_armies)
    engine = GameEngine(state)

    ### =========================================== Start Actual Game
    if show_vis:
        run_w_vis(controllers, state, engine)
    else:
        while not engine.is_game_over():
            #print_board(engine.state)
            player_id = engine.state.current_player_id
            controller = controllers[player_id]
            action = controller.choose_action(engine.state)
            result = engine.apply_action(action)
            #print_action_result(result)

            # if it looks like bots aren't doing anything useful, end the game
            if engine.state.turn_number >= 500:
                break

        #print_board(engine.state)
        #print_game_over(engine.state)

        ## Get winner locally
        num_territories = [0, 0, 0, 0, 0, 0]
        for i in range(len(engine.state.players)):
            for territory in engine.state.territories.values():
                if territory.owner_id == engine.state.players[i].player_id:
                    num_territories[i] += 1
        print(num_territories)


def main():
    runGame()


if __name__ == "__main__":
    main()
