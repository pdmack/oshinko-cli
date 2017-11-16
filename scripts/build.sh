#!/bin/sh
set -ex
SCRIPT_DIR=$(readlink -f `dirname "$0"`)
. ${SCRIPT_DIR%/*}/sparkimage.sh

go get github.com/renstrom/dedent
go get github.com/docker/go-connections/nat
go get github.com/ghodss/yaml

CMD=${*: -1}
while getopts ":t:" option
do
  case "${option}" in
    t )
      if echo "${OPTARG}" | grep -v '[0-9]' >/dev/null 2>&1; then
        echo 'tag unspecified or invalid, will try from .git'
      else 
        TAG=$OPTARG
      fi
      shift $((OPTIND -1))
      ;;
    \? )
      echo "invalid option: -$OPTARG" 1>&2
      exit 1
      ;;
    : )
      echo "invalid option: -$OPTARG requires a tag" 1>&2
      exit 1
      ;;
  esac
done

PROJECT='github.com/radanalyticsio/oshinko-cli'
if [ -z $TAG ]; then
  TAG=`git describe --tags --abbrev=0 2> /dev/null | head -n1`
  GIT_COMMIT=`git log -n1 --pretty=format:%h`
  TAG="${TAG}-${GIT_COMMIT}"
fi

APP=oshinko

OUTPUT_DIR="_output"
OUTPUT_PATH="$OUTPUT_DIR/$APP"
OUTPUT_FLAG="-o $OUTPUT_PATH"
TARGET=./cmd/oshinko

# this export is needed for the vendor experiment for as long as go version
# 1.5 is still in use.
export GO15VENDOREXPERIMENT=1
if [ $CMD = build ]; then
  go build $GO_OPTIONS -ldflags \
    "-X $PROJECT/version.gitTag=$TAG -X $PROJECT/version.appName=$APP -X $PROJECT/version.sparkImage=$SPARK_IMAGE"\
    -o $OUTPUT_PATH $TARGET
  if [ "$?" -eq 0 ]; then
    rm $OUTPUT_DIR/oshinko-cli || true
    ln -s ./oshinko $OUTPUT_DIR/oshinko-cli
  fi
fi
