#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

set -e

rm -rf python36 && mkdir -p python36

pushd python36

wget "https://github.com/vial-kb/vial-deps/releases/download/v1/Python-3.6.15.tar.xz"
tar xvf Python-3.6.15.tar.xz

pushd Python-3.6.15
./configure --enable-shared --prefix=$SCRIPT_DIR/python36/prefix/
make -j4
make install
popd

popd
