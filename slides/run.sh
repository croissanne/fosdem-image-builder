#!/bin/bash

reveal-md ./slides.md --theme serif --watch --css ./style.css --disable-auto-open &
REVEAL_PID=$!

ff -P fosdem localhost:1948/slides.md

kill $REVEAL_PID
