#!/bin/bash

set -e 

EXE="../souper/third_party/llvm-Release-install/bin/clang"
BCFLAGS="-emit-llvm -c -o"
LLFLAGS="-S -emit-llvm -o"
INPUT_FILE="$1"
BCFILE="${INPUT_FILE%.*}.bc"
LLFILE="${INPUT_FILE%.*}.ll"

# command to generate bytecode
$EXE $BCFLAGS $BCFILE $INPUT_FILE

# command to generate llvm assembly
$EXE $LLFLAGS $LLFILE $INPUT_FILE
