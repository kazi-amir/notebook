#!/bin/bash
set -e

### COMMON SETUP; DO NOT MODIFY ###

run_all_tests() {
    # Run the specific unit tests for ComInterfaceGenerator directly to stdout/stderr
    ./dotnet.sh test src/libraries/System.Runtime.InteropServices/tests/ComInterfaceGenerator.Unit.Tests/ComInterfaceGenerator.Unit.Tests.csproj -c Release --logger "console;verbosity=detailed"
}

### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests