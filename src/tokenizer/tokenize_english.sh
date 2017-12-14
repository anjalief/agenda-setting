#!/bin/bash

mkdir -p /tmp/tokenize_anjalie

NEWS=$1

for f in ${NEWS} ; do
  echo $f
  base_f=`basename $f`
  new_name=${f/ytsvetko/anjalief}
  dir_name=`dirname ${new_name}`
  mkdir -p $dir_name

  # for russian we do more stuff, but this should be
  # good enough for english
  ./tokenize-anything.sh < $f  > "${new_name}".tok
done
