#!/bin/bash -e

# This file is part of f/π
#
# Copyright (C) 2020 Rafael Guterres Jeffman
#
# f/π is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <https://www.gnu.org/licenses/>.

cleanup() {
    if [ "${PYTHON_ENV}" == "no" ]
    then
        deactivate > /dev/null 2>&1
    fi
}

check_failed() {
    cleanup
    echo "FAILED: fix any failure before commiting code."
    exit 1
}

trap cleanup EXIT SIGINT SIGKILL
trap check_failed ERR

quiet() {
    $* >/dev/null 2>&1
}

verify_black() {
    echo -n "black check... "
    if black -l 79 -t py38 --check $*
    then
        echo ""
        return 0
    else
        echo "FAILED (although `black` is not yet a requirement, it soon will be.)"
        return 1
    fi
}

verify_flake8() {
    echo -n "Runing flake8... "
    ${PYTHON} -m flake8 $*
    res=$?
    echo "done."
    return $res
}

verify_pylint() {
    MIN_SCORE=$1
    shift 1
    echo -n "pylint (you'll need a score of at least ${MIN_SCORE})... "
    INT_VALUE=`echo "print(int(${MIN_SCORE}))" | ${PYTHON}`
    ${PYTHON} -m pylint -r y -s y --fail-under=${INT_VALUE} $*
    res=$?
    echo "done."
    return $res
}

verify_code_format() {
    local FILES=`echo "$*" | tr " " "\n" | sort | uniq`
    [ -z "$MIN_SCORE" ] && MIN_SCORE=10
    echo "Code format check"
    verify_black ${FILES} || true
    verify_flake8 ${FILES}
    verify_pylint ${MIN_SCORE} ${FILES}
}

verify_yaml_syntax()  {
    failed=0
    while [ ! -z "$1" ]
    do
        local YAML_FILE="$1"
        shift
        echo -n "Checking YAML syntax for '$1'..."
        ${PYTHON} -c "with open('${YAML_FILE}') as f: import yaml; yaml.safe_load(f)"
        [ $failed -eq 0 ] && failed=$?
        [ $failed -eq 0 ] && echo "DONE." || echo "FAILED"
    done
    return $failed
}

ensure_python_virtualenv() {
    PYTHON_ENV=$(${PYTHON} -c "import sys; print('yes' if hasattr(sys, 'real_prefix') else 'no')")

    if [ "${PYTHON_ENV}" == "no" ]
    then
        if [ ! -d ".venv" ]
        then
            quiet ${PYTHON} -m virtualenv .venv
        fi
        . .venv/bin/activate
    fi
}

check_python_interpreter() {
    local PYTHON
    PYTHON=`which python`
    declare -a PYVERSION=(`python --version | cut -d" " -f2 | sed "s/\./ /g"`)
    MAJOR=${PYVERSION[0]}
    MINOR=${PYVERSION[1]}
    [ "${MAJOR}" = "2" ] && PYTHON=`which python3`
    echo ${PYTHON}
}

install_required_packages() {
    quiet ${PYTHON} -m pip install pylint pyyaml black
    if [ -f "requirements.txt" ]
    then
        quiet ${PYTHON} -m pip install -r requirements.txt
    fi
    if [ ! -z "${CODECHECK_REQ}" ]
    then
        [ -f "${CODECHECK_REQ}" ] && quiet ${PYTHON} -m pip install -r ${CODECHECK_REQ}
    fi
}

dir=`dirname $0`
. ${dir}/codecheck.cfg

PYTHON=`check_python_interpreter`

MIN_SCORE='10.0'

ensure_python_virtualenv

install_required_packages

for YAML_FILE in ${CODECHECK_YAML}
do
    echo -n "Checking YAML syntax for ${YAML_FILE}..."
    verify_yaml_syntax ${YAML_FILE}
    echo "DONE."
done

if [ "$1" == "--fast" -o "$1" == "-f" ]
then
    FILES=(`git status -s | sed "
    /^R/d
    s/...\(.*\)/\1/
    " | grep "py$" || true`)
elif [ -z "$*" ]
then
    FILES=()
    for srcdir in ${CODECHECK_DIRS[@]}
    do
        FILES+=(`find ${srcdir} -name "*.py"`)
    done
else
    FILES="$*"
fi

if [ ${#FILES[@]} -gt 0 ]
then
    verify_code_format ${FILES[@]}
else
    echo "No Python file to verify."
fi
