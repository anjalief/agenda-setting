#!/bin/bash

included_topics=(
Arts
RealEstate
Travel
Sports
HomeandGarden
Food
Business
Automobiles
DiningandWine
Movies
Obituaries
JobMarket
World
Theater
DiningWine
Science
Style
YourMoney
Autos
Washington
US
Books
Health
Education
Technology
)

excluded_topics=(
PublicEditor
Booming
TimesInsider
NewYork
Unknown
Multimedia
NYTNow
NewYorkandRegion
Corrections
Day
Olympics
GreatHomesandDestinations
TimesTopics
TimesMachine
NYRegion
TimesMachine
AfternoonUpdate
Fashion
SundayReview
Blogs
PaidDeathNotices
Topics
HomeGarden
Universal
MultimediaPhotos
Magazine
TodaysPaper
WeekInReview
Corrections
Opinion
TheUpshot
CrosswordsGames
GreatHomesDestinations
Open
National
InternationalHome
College
WeekinReview
Learning
FrontPage
Giving
)


FILES=/projects/tir1/users/anjalief/all_nyt_paras_text/*
TEST_DIR=/projects/tir1/users/anjalief/nyt_filtered/
RESERVED_DIR=/projects/tir1/users/anjalief/nyt_held_out/

ALL_FILES=
index=1

for f in $FILES
do
make=0
    base_f=`basename $f`
    for i in ${included_topics[@]}; do
	if [[ $base_f == *"$i"* ]]; then
	    make=1
        fi
    done
    # make sure it doesn't contain anything we are
    # actively excluding
    if [ "$make" -eq "1" ]; then
        for i in ${excluded_topics[@]}; do
	    if [[ $base_f == *"$i"* ]]; then
	        make=0
            fi
        done
    fi
    # create directories
    if [ "$make" -eq "1" ]; then
        for file in $f/*.tok
        do
            ALL_FILES[$index]=$file
            let "index += 1"
        done
            mkdir -p "$TEST_DIR$base_f"
            mkdir -p "$RESERVED_DIR$base_f"
    fi
done

# now choose 20% of the files as heldout data
let "num_reserve=$index/5"

count=1
while [ "$count" -le $num_reserve ]
do
  # keep trying until we get a new one
  let "number=$RANDOM % $index"
  while [[ ${ALL_FILES[$number]} == "" ]]
  do
      let "number=$RANDOM % $index"
  done
  # sym link file to test data
  old_name=${ALL_FILES[$number]}
  new_name=${old_name/all_nyt_paras_text/nyt_held_out}
  ln -snf $old_name $new_name
  ALL_FILES[$number]=""
  let "count += 1"  # Increment count.
done


# for all the files we didn't reserve, sym link them to the
# filtered dir
num_test=1
for i in ${ALL_FILES[@]}; do
    if [[ $i != "" ]]; then
        old_name=$i
        new_name=${old_name/all_nyt_paras_text/nyt_filtered}
        ln -snf $old_name $new_name
        let "num_test += 1"
    fi
done

# index = num_test + num_reserve
echo $num_test
echo $num_reserve
echo $index