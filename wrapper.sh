#!/bin/bash

if [ -z "$JOBBERGATE_PATH" ]; then
    export JOBBERGATE_PATH="<pathtojobbergate>"
fi

# Find out name of wrapper
wrappername=$(basename $0)

# Remove .sh at the end if it exists, otherwise do notihing
applicationname=${wrappername%%.sh}

flask $applicationname $@
