import os
import random
import textwrap
import time
from datetime import timedelta, datetime

from textlib import (
    riddles,
    room_name,
    caught_not_holding,
    cop_text,
    descriptions,
    visited_lab_text,
    room_text,
)

# text formatting
wrapper = textwrap.TextWrapper(
    width=77,
    initial_indent="   ",
    subsequent_indent="   ",
    break_long_words=False,
)

wrap_indent_more = textwrap.TextWrapper(
    width=77,
    initial_indent="        ",
    subsequent_indent="        ",
    break_long_words=False,
)


# A collection of colors and text effects to use.
class bcolors:
    PURPLE = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def title():
    """Just a pretty to open the game."""

    print(wrapper.fill(text="") + "\n")
    print(
        f"     {bcolors.CYAN}PPP{bcolors.ENDC}     {bcolors.RED}AA{bcolors.ENDC}    {bcolors.BLUE}RRR{bcolors.ENDC}    {bcolors.YELLOW}TTT{bcolors.ENDC}   {bcolors.GREEN}SSSS{bcolors.ENDC}"
    )
    time.sleep(0.07)
    print(
        f"     {bcolors.CYAN}P  P{bcolors.ENDC}   {bcolors.RED}A  A{bcolors.ENDC}   {bcolors.BLUE}R  R{bcolors.ENDC}    {bcolors.YELLOW}T{bcolors.ENDC}    {bcolors.GREEN}S{bcolors.ENDC}"
    )
    time.sleep(0.07)
    print(
        f"     {bcolors.CYAN}PPP{bcolors.ENDC}    {bcolors.RED}AAAA{bcolors.ENDC}   {bcolors.BLUE}RRR{bcolors.ENDC}     {bcolors.YELLOW}T{bcolors.ENDC}    {bcolors.GREEN}SSSS{bcolors.ENDC}"
    )
    time.sleep(0.07)
    print(
        f"     {bcolors.CYAN}P{bcolors.ENDC}      {bcolors.RED}A  A{bcolors.ENDC}   {bcolors.BLUE}R R{bcolors.ENDC}     {bcolors.YELLOW}T{bcolors.ENDC}       {bcolors.GREEN}S{bcolors.ENDC}"
    )
    time.sleep(0.07)
    print(
        f"     {bcolors.CYAN}P{bcolors.ENDC}      {bcolors.RED}A  A{bcolors.ENDC}   {bcolors.BLUE}R  R{bcolors.ENDC}    {bcolors.YELLOW}T{bcolors.ENDC}    {bcolors.GREEN}SSSS{bcolors.ENDC}"
    )
    time.sleep(0.07)
    print(wrapper.fill(text="") + "\n")


class Map:
    """A class for making the map"""

    def __init__(self, num_rooms=17, min_edges_per_node=2):
        self.num_rooms = num_rooms
        self.min_edges_per_node = min_edges_per_node

    def get_map(self):
        """This function creates the game board.
        It is hard coded to produce 'num_rooms' rooms, and randomly creates connections between them.
        Each room has to have at least min_edges_per_node doors (connections), and through playing the game I have seen 3-5 doors.
        """

        graph = {}
        for i in range(self.num_rooms):
            graph[i] = []
        options = [j for j in range(self.num_rooms)]
        k = 0
        while len(options) > 1:
            options.remove(k)
            pick = random.choice(options)
            graph[k].append(pick)
            graph[pick].append(k)
            k = pick

        for i in range(self.num_rooms):
            options = [j for j in range(self.num_rooms)]
            options.remove(i)
            for j in graph[i]:
                options.remove(j)
            while len(graph[i]) < self.min_edges_per_node:
                pick = random.choice(options)
                options.remove(pick)
                graph[i].append(pick)
                graph[pick].append(i)
        return graph


class PlayField:
    """A class that sets all the initial game settings when called from main."""

    # declare
    start_time = datetime.now()
    map = None
    items = {}
    rooms_not_visited = []
    riddles_to_use = []
    cop1_loc = 0
    cop2_loc = 0
    in_room = 0

    def __init__(
        self,
        num_rooms=17,
        min_edges_per_node=3,
        num_cops=1,
        time_limit_seconds=600,
        timed=False,
    ):
        """Initiates the game, and sets up many of the needed settings and lists."""

        self.num_rooms = num_rooms
        self.min_edges_per_node = min_edges_per_node
        self.num_cops = num_cops
        self.time_limit_seconds = time_limit_seconds
        self.timed = timed

        map_create = Map(self.num_rooms, self.min_edges_per_node)
        self.map = map_create.get_map()

        key_rooms_choices = [i for i in range(1, self.num_rooms)]
        for i in descriptions:
            key = random.choice(key_rooms_choices)
            self.items[i] = (key, 0)
            key_rooms_choices.remove(key)

        self.rooms_not_visited = [i for i in range(self.num_rooms)]

        self.riddles_to_use = [i for i in range(len(riddles))]

        cop_room_list = [i for i in range(1, self.num_rooms)]
        self.cop1_loc = random.choice(cop_room_list)
        cop_room_list.remove(self.cop1_loc)
        self.cop2_loc = random.choice(cop_room_list) if self.num_cops == 2 else -1


class Game(PlayField):
    """The game. Inherits the settings created in PlayField. This is the transactions class."""

    def move_cops(self):
        """Move the cops to an adjacent place. Cops cannot move to the lab, or into the same location at the same time."""

        p = 0
        while p == 0:
            p = random.choice(self.map[self.cop1_loc])
        self.cop1_loc = p

        if self.cop2_loc >= 1:
            p = 0
            while p == 0 or p == self.cop1_loc:
                p = random.choice(self.map[self.cop2_loc])
            self.cop2_loc = p
        return self.cop1_loc, self.cop2_loc

    def get_move_options(self):
        """Returns the places the player can move to from their current location."""

        return self.map[self.in_room]

    def set_loc(self, new_loc):
        """Record the player's move"""

        self.in_room = new_loc

    def check_end_game(self):
        """Checks if any of the end game criteria has been met, and returns the end game status."""

        game_status = 0
        if self.in_room == 0:
            count = 1
            for item in self.items:
                room, status = self.items[item]
                count *= status
                if status == 1:
                    self.items[item] = (room, 2)
            if count != 0:
                game_status = 1
        if self.in_room == self.cop1_loc or self.in_room == self.cop2_loc:
            holding = False
            for item in self.items:
                room, status = self.items[item]
                if status == 1:
                    holding = True
            if holding:
                game_status = 3
        end_time = datetime.now()
        if self.timed and (end_time - self.start_time) >= timedelta(
            seconds=self.time_limit_seconds
        ):
            game_status = 2
        return game_status

    def show_room_name(self):
        """Prints the room name."""

        print(
            wrapper.fill(text=f"{bcolors.BOLD}{room_name[self.in_room]}{bcolors.ENDC}")
            + "\n"
        )

    def show_room_desc(self):
        """Prints the current room's desc, either new or already visited. Marks room as visited."""

        if self.in_room in self.rooms_not_visited:
            for i in room_text[self.in_room]:
                time.sleep(0.07)
                print(wrapper.fill(text=i) + "\n")
            self.rooms_not_visited.remove(self.in_room)
        else:
            if self.in_room == 0:
                for i in visited_lab_text:
                    time.sleep(0.07)
                    print(wrapper.fill(text=i) + "\n")
            else:
                print(
                    wrapper.fill(
                        text="There are no parts here that are fresh enough to harvest."
                    )
                    + "\n"
                )

    def check_items(self):
        """Checks whether the current room has an item that hasn't been picked up, and prints the desc."""

        for item in self.items:
            room, status = self.items[item]
            if self.in_room == room and status == 0:
                time.sleep(0.07)
                print(wrapper.fill(text=descriptions[item]) + "\n")

    def take_item(self):
        """Checks whether the current room has an item that hasn't been picked up, then picks it up and puts it in the inventory."""

        for item in self.items:
            room, status = self.items[item]
            if self.in_room == room and status == 0:
                self.items[item] = (room, 1)

    def question_item(self):
        """Checks whether the current room has an item that hasn't been picked up, then returns text to use in the next action question."""

        return_text = ""
        for item in self.items:
            room, status = self.items[item]
            if self.in_room == room and status == 0:
                return_text += f"take {item}"
        return return_text

    def get_items(self):
        """Grabs the list of items."""

        return self.items

    def show_doors(self, game):
        """This function displays the available doors in the room. And displays the distance to cops."""

        options = game.get_move_options()
        num_doors = len(options)
        time.sleep(0.07)
        print(
            wrapper.fill(
                text=f"From here you can sneak to {str(num_doors)} places. Remember to stay low, stay quiet."
            )
            + "\n"
        )
        time.sleep(0.07)
        print(wrapper.fill(text="The places you think you could safely get to:") + "\n")
        for i in options:
            time.sleep(0.07)
            print(
                wrapper.fill(
                    text=f"{bcolors.BOLD}{str(i)}), {room_name[i]}{bcolors.ENDC}"
                )
            )
            print(wrap_indent_more.fill(text=f"-- {game.show_cop_distance(i)}") + "\n")

    def show_caught_by_cops(self):
        """Displays the 'caught by cops' text, when the user is not holding any body parts."""

        if self.in_room == self.cop1_loc:
            time.sleep(0.07)
            print(wrapper.fill(text=cop_text[0]) + "\n")
            for i in caught_not_holding:
                time.sleep(0.07)
                print(wrapper.fill(text=i) + "\n")
            time.sleep(0.07)
            print(input(wrapper.fill(text="Press enter to continue")) + "\n")
            os.system("cls||clear")
            print("\n")
        elif self.cop2_loc >= 1:
            if self.in_room == self.cop2_loc:
                time.sleep(0.07)
                print(wrapper.fill(text=cop_text[0]) + "\n")
                for i in caught_not_holding:
                    time.sleep(0.07)
                    print(wrapper.fill(text=i) + "\n")
                time.sleep(0.07)
                print(input(wrapper.fill(text="Press enter to continue")) + "\n")
                os.system("cls||clear")
                print("\n")

    def show_cop_distance(self, room):
        """Checks the distance to the cops, and displays a warning when getting close."""

        return_text = ""
        if self.cop1_loc == room or self.cop2_loc == room:
            return_text += f"{bcolors.RED}You can hear loud footsteps coming from {room_name[room]}{bcolors.ENDC}"
        else:
            for i in self.map[room]:
                if self.cop1_loc == i or self.cop2_loc == i:
                    return_text += f"{bcolors.YELLOW}You can hear faint footsteps coming from somewhere beyond {room_name[room]}{bcolors.ENDC}"
                    break
        if return_text == "":
            return_text += f"{bcolors.BLUE}All is quiet in the direction of {room_name[room]}{bcolors.ENDC}"
        return return_text

    def get_riddles_to_use(self):
        """Grabs the riddles_to_use list."""

        return self.riddles_to_use

    def update_riddles_to_use(self, riddle):
        """When a riddle is used, remove it from the riddles_to_use list. When the list is empty, recreates it."""

        self.riddles_to_use.remove(riddle)
        if len(self.riddles_to_use) == 0:
            self.riddles_to_use = [i for i in range(len(riddles))]

    def dis_inventory(self):
        """Display the inventory at each turn"""

        text = ""
        for item in self.items:
            room, status = self.items[item]
            text += "        " + item + ": "
            if status == 0:
                text += "\n"
            elif status == 1:
                text += f"{bcolors.YELLOW}Holding{bcolors.ENDC}\n"
            else:
                text += f"{bcolors.BLUE}Delivered{bcolors.ENDC}\n"
        return text

    def collect_paths(self, me, locs, game, seen):
        """Recursive function that finds the path from the current location to the closest key room. Return the next, best direction."""
        seen.append(me)
        for i in self.map[me]:
            if i in locs:
                return i
        for i in self.map[me]:
            if i not in seen:
                if game.collect_paths(i, locs, game, seen) >= 0:
                    return i

    def shortest_path(self, game):
        """Creates a list of locations that still holds a key, or if none, puts in 0 for the lab. Grabs the current location.
        Then sends them to the recursive function to step through the paths."""

        locations = [0]
        for item in self.items:
            room, status = self.items[item]
            if status == 0:
                locations.append(room)
        if len(locations) > 1:
            locations.remove(0)
        next_step = game.collect_paths(self.in_room, locations, game, seen=[])
        return next_step

    def give_hint(self, riddle_id, game):
        """A function that asks a riddle and gives a hint when the player gets the answer correct."""

        riddle, answer = riddles[riddle_id]
        print("\n")
        time.sleep(0.07)
        print(
            wrapper.fill(
                text="At a loss of which way to go next, you open your 'Little Useful Book' at a random page."
            )
            + "\n"
        )
        time.sleep(0.07)
        print(wrapper.fill(text="You read:") + "\n")
        time.sleep(0.07)
        print(wrapper.fill(text=riddle) + "\n")
        time.sleep(0.07)
        ans = input(wrapper.fill(text="And what would be your one-word reply?") + " ")
        print("\n")
        time.sleep(0.07)
        if ans in answer and ans != "" and ans != " ":
            print(
                wrapper.fill(
                    text=f"{bcolors.CYAN}In your mind forms a number:{bcolors.ENDC} {bcolors.BOLD}{str(game.shortest_path(game))}{bcolors.ENDC} {bcolors.CYAN}"
                    + f"This is the first step in the shortest route to your goal, but you must still be aware of the cop.{bcolors.ENDC}"
                )
                + "\n"
            )
        else:
            print(
                wrapper.fill(
                    text=f"{bcolors.RED}Your 'little Useful Book' is not being cooperative, and is not giving you a hint.{bcolors.ENDC}"
                )
                + "\n"
            )
