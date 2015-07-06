#!/bin/bash

i=0

while [ $i -lt 500 ]
do
    python3 tests.py &

    echo $i

    i=$[$i + 1]
done
