#!/usr/bin/env bash

python split_data.py
python createTrainTest.py
python classifier.py
python NBClassifier.py
python NBtesting.py
python customClassifier.py
