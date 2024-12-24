# Jason Padgett
# IT 140 Project Two
# This was written originally in 3 files: a text library, a function and class library, and then a file for the main function.
# All in one file is pretty long, so after submission, I will separate it back out.
# All text and code by Jason Padgett, except where indicated

import os
import random
import time

from codelib import title, wrapper, Game, bcolors
from textlib import game_text, cop_text, caught_holding


def main():
    # Initial settings needed to start the game.
    game_status = (
        0  # 0 is an active game, other numbers indicate different types of endings
    )
    time_limit_seconds = 600  # seconds in the timed game
    num_rooms = 17  # The total number of locations on the game board.
    min_edges_per_node = (
        3  # This sets the minimum number of paths a single location can have
    )
    message = None

    os.system("cls||clear")

    # Display the title
    title()

    # ask about timed game
    time.sleep(0.07)
    timed = (
        True
        if input(
            wrapper.fill(
                text="Would you like to try a timed run? Set at 10 mins. y / n: (n)"
            )
            + " "
        ).lower()
        == "y"
        else False
    )
    print()

    # ask about number of cops
    time.sleep(0.07)
    print(wrapper.fill(text="How many cops would you like to try to avoid:") + "\n")
    time.sleep(0.07)
    cops = input(wrapper.fill(text="1) fairly simple, 2) a bit harder: (1)") + " ")
    num_cops = int(cops) if cops.isnumeric() else 1
    num_cops = 2 if num_cops >= 2 else 1
    print()

    # play the game
    os.system("cls||clear")
    print("\n")
    for i in game_text["opening"]:
        time.sleep(0.07)
        print(wrapper.fill(text=i) + "\n")
    time.sleep(0.07)
    print(input(wrapper.fill(text="Press enter to continue")) + "\n")

    # Create the game
    game = Game(num_rooms, min_edges_per_node, num_cops, time_limit_seconds, timed)

    # Start the game loop, and continue the loop until an end game has been reached
    while game.check_end_game() == 0:

        # a visual room break
        os.system("cls||clear")
        print("\n")
        if message is not None:
            time.sleep(0.07)
            print(message)
            print("\n")
        message = None

        # show the text if the player shares a location with a cop, and is not holding parts.
        game.show_caught_by_cops()

        # Print room name and description
        time.sleep(0.07)
        game.show_room_name()
        game.show_room_desc()

        # if a key is in this room, tick the appropriate inv item
        game.check_items()

        # display inventory
        time.sleep(0.07)
        print(game.dis_inventory() + "\n\n")

        # show available doors
        time.sleep(0.07)
        game.show_doors(game)

        # collect the next move
        tick_cops = True
        while True:
            ques = game.question_item()
            if ques != "":
                question = "'" + ques + "', "
                answer = ques
            else:
                question = ""
                answer = ""
            time.sleep(0.07)
            room_choice = input(
                wrapper.fill(
                    text=f"Please enter location number, {bcolors.YELLOW}{question}{bcolors.ENDC}'hint', 'stay', or 'exit':"
                )
                + " "
            )
            room_choice.strip()
            time.sleep(0.07)

            # If there is an item in the room, the option to pick it up is active
            if answer != "" and str(room_choice).lower() == answer:
                game.take_item()
                text_split = answer.split(" ")
                item_name = text_split[1]
                print("\n")
                desc = "it" if item_name in ["head", "torso", "brain"] else "them"
                message = wrapper.fill(
                    text=f"{bcolors.YELLOW}You take the {item_name} and put {desc} in your sack.{bcolors.ENDC}"
                )
                tick_cops = False
                break

            # If the player wants a hint, show a riddle, process the answer, show the hint.
            elif str(room_choice).lower() == "hint":
                riddle = random.choice(game.get_riddles_to_use())
                game.update_riddles_to_use(riddle)
                game.give_hint(riddle, game)

            # If the player doesn't want to move this turn.
            elif str(room_choice).lower() == "stay":
                print(
                    wrapper.fill(text="You decide your best move is not to move.")
                    + "\n"
                )
                break

            # If the player wants out of the game, set game status, break out of loop.
            elif str(room_choice).lower() == "exit":
                game_status = 4
                tick_cops = False
                break

            # If input is a number, check if the place is available, then set the new location.
            elif room_choice.isnumeric():
                if int(room_choice) in game.get_move_options():
                    game.set_loc(int(room_choice))
                    break
                elif int(room_choice) < 0 or int(room_choice) > num_rooms:
                    print(
                        wrapper.fill(
                            text="That is an invalid location. Maybe it is a location in a different village."
                        )
                        + "\n"
                    )
                else:
                    print(
                        wrapper.fill(
                            text="It would too risky to try and go there from here."
                        )
                        + "\n"
                    )

            # If the input doesn't fall into any of the above criteria, print invalid choice and re-loop.
            else:
                print(wrapper.fill(text="Invalid choice") + "\n")

        # move the cops randomly
        if tick_cops:
            game.move_cops()

        # If the player requested out of the game, break out of the game loop.
        if game_status > 0:
            break

    # end game text
    os.system("cls||clear")
    end_game = game.check_end_game()
    print("\n")

    # You Won! #
    if end_game == 1:
        for i in game_text["winning"]:
            time.sleep(0.07)
            print(wrapper.fill(text=i) + "\n")
            print("\n")

    # You lost to the timer.
    elif end_game == 2:
        for i in game_text["losing_time"]:
            time.sleep(0.07)
            print(wrapper.fill(text=i) + "\n")
            print("\n")

    # You were caught by the popo.
    elif end_game == 3:
        time.sleep(0.07)
        print(wrapper.fill(text=cop_text[0]) + "\n")
        for i in caught_holding:
            time.sleep(0.07)
            print(wrapper.fill(text=i) + "\n")
        for i in game_text["losing_cop"]:
            time.sleep(0.07)
            print(wrapper.fill(text=i) + "\n")
            print("\n")

    # Generic game over.
    else:
        time.sleep(0.07)
        print(wrapper.fill(text="Game over") + "\n")
        print("\n")


main()
