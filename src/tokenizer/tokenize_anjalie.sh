#!/bin/bash

mkdir -p /tmp/tokenize_anjalie

NEWS=$1

for f in ${NEWS} ; do
  echo $f
  base_f=`basename $f`
  new_name=${f/ytsvetko\/projects/anjalief}
  dir_name=`dirname ${new_name}`
if [ ! -d "$dir_name" ]; then
  # Control will enter here if $DIRECTORY doesn't exist.
    mkdir $dir_name
fi
  tmp_out="/tmp/tokenize_anjalie/${base_f}"
  ./tokenize-anything.sh < $f  | ./utf8-normalize.sh  > "${tmp_out}"
  ./normalize.py "${tmp_out}" "${new_name}.tok"
done
