from __future__ import annotations

from asp.generate_information import call_dlv_handler, update_world_information
from game.actions import AttackAction, MoveAction, ConquerAction, EndPhaseAction, PlaceArmiesAction
from game.models import GameState, Phase
from game.rules import get_territories_owned_by
from players.base import PlayerController


class BasicASPPlayer(PlayerController):
    def choose_action(self, state: GameState):
        # if we have no territories, we have been defeated, and will skip our turn
        if len(get_territories_owned_by(state, self.player_id)) == 0:
            return EndPhaseAction()

        if state.current_phase == Phase.REINFORCE:
            return self._choose_reinforcement(state)
        return self._choose(state)

    def _choose_reinforcement(self, state: GameState) -> PlaceArmiesAction:
        ## if the agent already chose reinforcements that haven't been processed yet,
        ##  grab the next one from the inner list
        if len(self.reinforcement_moves) != 0:
            territory = self.reinforcement_moves[0][0]
            count = self.reinforcement_moves[0][1]
            self.reinforcement_moves = self.reinforcement_moves[1:]
            return PlaceArmiesAction(territory, count)
        ## get information from world to feed into DLV program
        info = update_world_information(self.player_id, "fortify", state.territories.values(), "to_fortify("+str(state.reinforcements_remaining)+").")
        #info.append()

        ## run DLV program to determine reinforcement choice(s)
        result = self._run_dlv_logic("fortify", info)

        ## handle the first (potentially only) fortify request
        territory = result[0][0]
        count = result[0][1]
        self.reinforcement_moves = result[1:]
        return PlaceArmiesAction(territory, count)

    def _choose(self, state: GameState):
        ## clear out reinforcement moves if there were still moves being saved
        self.reinforcement_moves = []
        ## get information from world to feed into DLV program
        info = update_world_information(self.player_id, str(state.current_phase.name).lower(), state.territories.values(), "")
        
        ## if we're in the conquer phase, let the agent know from where and to where
        if str(state.current_phase.name).lower() == "conquer":
            info.append("conquered("+state.last_attack_source.name+","+state.last_attack_target.name+").")
        
        ## run DLV program to determine next attack/move/pass choice
        result = self._run_dlv_logic(str(state.current_phase.name).lower(), info)

        ## if phase is conquer, parse properly
        if str(state.current_phase.name).lower() == "conquer":
            return ConquerAction(result)

        ## if the agent chooses to pass (or an error occurs), instantly end the turn
        ##  to keep the game going
        if result == "pass" or result == "error":
            return EndPhaseAction()
        
        ## if the agent chooses to attack, take their response (in (source, target) format)
        if result[0] == "attack":
            #print(result[1], result[2])
            return AttackAction(result[1], result[2])
        
        ## if the agent chooses to move, take their response (in (source, target, num) format)
        if result[0] == "move":
            return MoveAction(result[1], result[2], result[3])
        
    def _run_dlv_logic(self, phase: str, information: list):
        filter = "--filter=fortify/2,attack/2,move/3,pass/0,error/0"
        if phase == "fortify":
            filter = "--filter=fortify/2"
        elif phase == "choose":
            filter = "--filter=attack/2,move/3,pass/0,error/0"
        elif phase == "conquer":
            filter = "--filter=move/3"

        response = call_dlv_handler(self.rules_file, information, filter)
        print(response)

        # parse response
        if response == "ERROR":
            # something bad occurred, and it wasn't my fault (probably)
            print("############################## ASP not correct ##############################")
            return "error"
        
        ##################################### INCOHERENT for student testing ##################
        if response == None:
            print("######### INCOHERENT ANSWER SET ENCOUNTERED #########")
            quit()
        
        if phase == "fortify":
            fortifies = []
            for f in response:
                if "fortify" in f:
                    target = f.split("(")[1].split(",")[0]
                    num = f.split(",")[1].split(")")[0]
                    fortifies.append([target, int(num)])
            return fortifies
        # if we are in the "choose" portion, parse the decision
        if phase == "choose":
            for f in response:
                if f == "pass":
                    return f
                if f == "error":
                    return f
                ## if attack is the predicate, grab the source and target
                if "attack" in f:
                    source = f.split("(")[1].split(",")[0]
                    target = f.split(",")[1].split(")")[0]
                    return ["attack", source, target]
                ## if move is the predicate, grab the source, target, and num to move
                if "move" in f:
                    running = f.split("(")[1]
                    source = running.split(",")[0]
                    target = running.split(",")[1]
                    num = running.split(",")[2].split(")")[0]
                    print(source, target, num)
                    return["move", source, target, int(num)]
        ## if we're in the conquer phase, return the number the agent chose to move
        if phase == "conquer":
            for f in response:
                return int(f.split(",")[2].split(")")[0])

        ## if we got this far, something went wrong/unexpected, so return an error
        return "error"