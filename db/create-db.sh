#!/bin/bash
rm trim-it-right.db
cat $1 | sqlite3 trim-it-right.db
