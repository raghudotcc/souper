#!/bin/bash

SEXE=../souper/souper-build/souper
CEXE=../souper/souper-build/souper-check

# if $1 is check, use CEXE, otherwise use SEXE
if [ "$1" = "--check" ]; then
    EXE=$CEXE
else
    EXE=$SEXE
fi

if [ "$1" = "--check" ]; then
    SOUPER_OPTIONS="${@:2:$(($#-2))}"
else
    SOUPER_OPTIONS="${@:1:$(($#-1))}"
fi
INPUTFILE="${@: -1}"

echo "$> $EXE $SOUPER_OPTIONS $INPUTFILE"

# run souper 
$EXE $SOUPER_OPTIONS $INPUTFILE

