#!/bin/bash

mkdir -p python
cd python
rm -rf *
pip3.9 install pandas -t .
pip3.9 install pathlib -t .
cd ..
zip -r sct-layers-python3.9.zip python
chmod 765 sct-layers-python3.9.zip
echo "created sct-layers-python3.9.zip..."
