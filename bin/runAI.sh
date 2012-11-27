#!/bin/bash

export PYTHONPATH="${PYTHONPATH}":"$(dirname "$0")"/../src/main/python

python -m maverick.players.ais.quiescenceSearchAI "${@}"
