#!/bin/bash

# TODO: Make sure this script works on the actual code. Works syntactically. 

# Declare weight variables
PIECE_WEIGHT=$[($RANDOM % 10)+1]
CHECK_WEIGHT=$[($RANDOM % 10)+1]
UNDER_ATTACK_WEIGHT=$[($RANDOM % 10)+1]
SPACE_COVERAGE_WEIGHT=$[($RANDOM % 10)+1]
PIECES_COVERED_WEIGHT=$[($RANDOM % 10)+1]

# Declare number of test groups to run
NUM_TEST_GROUPS=6

# Starts the server for the games
./runServer | tee runTestResults.txt


# Runs NUM_TEST_GROUPS tests to completion
for i in {1..$NUM_TEST_GROUPS}
do

	for (( i=0 ; i<12 ; i+2 ))
	do
		./runAI.sh $PIECE_WEIGHT $CHECK_WEIGHT $UNDER_ATTACK_WEIGHT $SPACE_COVERAGE_WEIGHT $PIECES_COVERED_WEIGHT &
		pidArray[i]=$!
		./runAI.sh $PIECE_WEIGHT $CHECK_WEIGHT $UNDER_ATTACK_WEIGHT $SPACE_COVERAGE_WEIGHT $PIECES_COVERED_WEIGHT &
		pidArray[i+1]=$!
	done

	# All tests started for this group. Wait on their completion
	# for each PID in array (loop through them) call wait(pid)
	for (( i=0 ; i<12 ; i++ ))
	do
		wait ${pidArray[i]}
	done
done
