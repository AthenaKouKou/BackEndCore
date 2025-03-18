#!/usr/local/bin/bash

TEMPL_DIR=$(pwd)
echo "Template directory: $TEMPL_DIR"

TEMPL_TEST_DIR="$TEMPL_DIR/tests"
TEMPL_PKG=templates
TEMPL_ENT=template
TEMPL_CLASS_PRE=Template
TEMPL_CONST=TEMPLATE

API_DIR=api
API_MOD_DIR="$API_DIR"
API_TEST_DIR="$API_DIR/tests"

if [ -z $1 ]; then
    echo "You must pass a repo dir to start from."
    exit 1
fi

echo "cd'ing into $1"
cd $1

echo "Enter the package for the new trio: "
read top_dir

if [ ! -d "$top_dir" ]; then
    echo "$top_dir does not exist, so creating it."
    mkdir $top_dir
else
    echo "$top_dir exists"
fi
imp_dir="$top_dir"
ep_mod="$top_dir"


echo "Enter the sub-package for the new trio: "
read sub_dir

new_dir=$top_dir
if [ ! -z $sub_dir ]
then
    new_dir="$new_dir"/"$sub_dir"
    if [ ! -d "$new_dir" ]; then
        echo "$new_dir does not exist, so creating it."
        mkdir $new_dir
    else
        echo "$new_dir exists"
    fi
    imp_dir="$top_dir.$sub_dir"
    echo "imp dir = $imp_dir"
    ep_mod="$top_dir"_"$sub_dir"
fi
echo $new_dir

new_test_dir="$new_dir"/tests
if [ ! -d "$new_test_dir" ]; then
    echo "$new_test_dir does not exist, so creating it."
    mkdir $new_test_dir
else
    echo "$new_test_dir exists"
fi

echo "Enter the data collection for the new trio: "
read entity
if [ -z "$entity" ]
then
      ent_str=''
else
      ent_str="$entity"
fi
new_class_pre="${ent_str^}"
new_const="${ent_str^^}"
echo $TEMPL_CONST
echo $new_const

# create the base trio files
cp $TEMPL_DIR/fields.py $new_dir/fields.py
cp $TEMPL_DIR/form.py $new_dir/form.py
echo "About to do these substitutions:"
echo "s/$TEMPL_DIR/$imp_dir/g"
echo "s/$TEMPL_ENT/$ent_str/g"
echo "s/$TEMPL_CONST/$new_const/g"
echo "s/$TEMPL_CLASS_PRE/$new_class_pre/g"
cat $TEMPL_DIR/query.py \
    | sed "s/$TEMPL_PKG/$imp_dir/g" \
    | sed "s/$TEMPL_ENT/$ent_str/g" \
    | sed "s/$TEMPL_CONST/$new_const/g" \
    | sed "s/$TEMPL_CLASS_PRE/$new_class_pre/g" \
    > $new_dir/query.py
cat $TEMPL_TEST_DIR/test_fields.py \
    | sed "s/$TEMPL_PKG/$imp_dir/g" \
    | sed "s/$TEMPL_CONST/$new_const/g" \
    | sed "s/$TEMPL_CLASS_PRE/$new_class_pre/g" \
    > $new_test_dir/test_fields.py
cat $TEMPL_TEST_DIR/test_form.py \
    | sed "s/$TEMPL_PKG/$imp_dir/g" \
    | sed "s/$TEMPL_CONST/$new_const/g" \
    | sed "s/$TEMPL_CLASS_PRE/$new_class_pre/g" \
    > $new_test_dir/test_form.py
cat $TEMPL_TEST_DIR/test_query.py \
    | sed "s/$TEMPL_PKG/$imp_dir/g" \
    | sed "s/$TEMPL_CONST/$new_const/g" \
    | sed "s/$TEMPL_CLASS_PRE/$new_class_pre/g" \
    > $new_test_dir/test_query.py

if [ ! -f "$new_dir"/makefile ]; then
    echo "makefile does not exist, so creating it."
    cat $TEMPL_PKG/makefile | sed "s/$TEMPL_PKG/$imp_dir/g" > $new_dir/makefile
else
    echo "makefile already exists."
fi

echo "Do you want to create API endpoints? (Y/N)"
read create_api

if [ $create_api == "Y" ] || [ $create_api == "y" ]; then
    new_ep_file=$API_MOD_DIR/$ep_mod.py
    new_ep_test_file=$API_TEST_DIR/test_$ep_mod.py
    # create the endpoint file
    if [ ! -f $new_ep_file ]; then
        echo "$new_ep_file file does not exist, so creating it."
        cat $API_MOD_DIR/templates.py \
            | sed "s/$TEMPL_DIR/$imp_dir/g" \
            | sed "s/$TEMPL_CONST/$new_const/g" \
            | sed "s/$TEMPL_CLASS_PRE/$new_class_pre/g" \
            > $new_ep_file
        cat $API_TEST_DIR/test_templates.py \
            | sed "s/$TEMPL_DIR/$imp_dir/g" \
            | sed "s/$TEMPL_DIR/$imp_dir/g" \
            | sed "s/$TEMPL_CONST/$new_const/g" \
            > $new_ep_test_file
    else
        echo "$new_ep_file already exists."
    fi
fi

# add new files to the repo
git add $new_dir/fields.py
git add $new_dir/form.py
git add $new_dir/query.py
git add $new_test_dir/test_fields.py
git add $new_test_dir/test_form.py
git add $new_test_dir/test_query.py
git add $new_dir/makefile
if [ $create_api == "Y" ] || [ $create_api == "y" ]; then
    git add $new_ep_file
    git add $new_ep_test_file
fi

