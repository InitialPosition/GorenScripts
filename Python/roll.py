import random
import argparse
import time

'''

======================================================

Copyright (C) 2019 Felix K.

Version 1.0

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


======================================================

'''


def main():
    # get a parser and set up commands
    parser = argparse.ArgumentParser(description='This script simulates dice rolls for the Goren DnD System.')

    parser.add_argument('--rolls', '-r', help='The amount of rolls (Default: 1)', default=1)
    parser.add_argument('--sides', '-s', help='The amount of sides the dice have (Default: 6)', default=6)
    parser.add_argument('--showHits', '-sH', help='Whether to show successful rolls (Default: false)',
                        action='store_true')
    parser.add_argument('--improvised', '-i', help='Whether the throw is improvised (Default: false)',
                        action='store_true')
    parser.add_argument('--finalStats', '-fS', help='Print timing stats at the end of execution (Default: false)',
                        action='store_true')
    parser.add_argument('--threshold', '-t', help='The threshold to succeed a d20 probe (Default: disabled)')
    parser.add_argument('--correction', '-c', help='The available correction points (Default: disabled)')

    args = parser.parse_args()

    # convert the given parameters to the correct data types
    try:
        args.rolls = int(args.rolls)
        args.sides = int(args.sides)
        if args.threshold is not None:
            args.threshold = int(args.threshold)
            args.correction = int(args.correction)

    # catch conversion errors by invalid parameters and show the user the help hint
    except ValueError:
        print("ERROR: Invalid parameters. Run 'roll.py -h' to get help.")
        exit(0)

    # start timer if stats were requested
    if args.finalStats:
        t0 = time.time()

    # declare some variables
    if args.threshold is None:
        hits = 0
        misses = 0

        dice_rolls = {}

        current_roll = 0

        # resize the dice roll list to the given dice size
        for i in range(args.sides):
            dice_rolls[i] = 0

        # roll the dice
        for i in range(args.rolls):
            current_roll = random.randint(1, args.sides)
            dice_rolls[current_roll - 1] = dice_rolls[current_roll - 1] + 1

            # collect hit / failure stats if parameter is given
            if args.showHits:
                if current_roll >= args.sides - 1:
                    hits = hits + 1
                if args.improvised:
                    if current_roll <= 2:
                        misses = misses + 1
                else:
                    if current_roll == 1:
                        misses = misses + 1

        # show the final stats if the parameter was given
        if args.showHits:
            print('HITS: ' + str(hits))
            print('FAILURES: ' + str(misses))

        # if there was only one roll requested, just print the result
        if args.rolls == 1:
            print(str(current_roll))

        # otherwise, print all results if they got rolled at least once
        else:
            for i in dice_rolls:
                if dice_rolls[i] != 0:
                    print(str(i + 1) + ': ' + str(dice_rolls[i]))
    else:
        # we are rolling a d20 probe
        rolls = {}
        successes = {}
        twenties = {}

        if args.rolls == 1:
            args.rolls = 3

        # roll the dice
        for i in range(args.rolls):
            rolls[i] = random.randint(1, 20)
            if rolls[i] == 20:
                twenties[i] = True
            else:
                twenties[i] = False

            if rolls[i] <= args.threshold:
                successes[i] = True
            else:
                successes[i] = False

        print('ROLLS: {0}'.format(rolls))
        # print('SUCCESSES: {0}'.format(successes))
        print('CORRECTION: {0}'.format(args.correction))

        # this is where we try to turn the highest possible amount of failures into successes
        # loop while optimization is still possible
        optimized = False
        if any(a for a in rolls):
            print('')
            print('OPTIMIZING...')
            while not optimized:
                lowest_failure = 21
                failure_id = -1
                # find the lowest failure
                print('')
                print('Determining lowest failed roll...')
                for i in range(args.rolls):
                    if lowest_failure > rolls[i] > args.threshold:
                        lowest_failure = rolls[i]
                        failure_id = i
                        print('New lowest failed roll: {0} (Roll ID {1})'.format(lowest_failure, failure_id))

                if failure_id is not -1:
                    # try to turn it into a success
                    needed_correction = lowest_failure - args.threshold
                    print('')
                    print('Correction points needed: {0}, points available: {1}'.format(needed_correction, args.correction))
                    if needed_correction <= args.correction:
                        args.correction = args.correction - needed_correction
                        rolls[failure_id] = rolls[failure_id] - needed_correction
                        successes[failure_id] = True
                        print('Roll {0} optimized'.format(failure_id))
                    else:
                        optimized = True
                        print('All rolls optimized')
                else:
                    optimized = True
                    print('All rolls optimized')

        # determine final data
        succs = 0
        fails = 0
        fixed_20s = 0

        for i in rolls:
            if successes[i]:
                succs = succs + 1

            if rolls[i] == 20:
                fails = fails + 1
            elif twenties[i]:
                fixed_20s = fixed_20s + 1

        # print the final probe result
        print('')
        print('FINAL RESULT: {0} SUCCESS(ES), {1} x 20, {2} x CORRECTED 20'.format(succs, fails, fixed_20s))

    # stop time and calculate speed
    if args.finalStats:
        t1 = time.time()
        delta_time = t1 - t0
        print('')
        if args.threshold is None:
            print('Executed {0} rolls in {1} seconds ({2} rolls / s)'.format(args.rolls, str(round(delta_time, 3)),
                                                                             str(round(args.rolls / delta_time, 2))))
        else:
            print('Executed probe in {0} seconds'.format(str(round(delta_time, 4))))


# program entry point
if __name__ == "__main__":
    main()
