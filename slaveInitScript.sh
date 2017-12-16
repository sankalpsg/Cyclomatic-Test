#!/bin/bash
echo "$1 is the url" 
echo "$2 is the commit sha" 

cd SlaveData

rm -rf .git/

git init
git remote add origin $1
git pull