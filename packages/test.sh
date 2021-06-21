#!/bin/bash
for entry in $(find . -type f -maxdepth 1) ; do
	   echo $entry
done
