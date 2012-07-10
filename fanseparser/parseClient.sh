#!/bin/bash

# This script (parseServer.sh) can be used to start a server for parsing
# See tratz.parse.SimpleParseServer and tratz.parse.SimpleParseClient classes

#$1 input file/dir
#$2 outputdir

#Note: It doesn't need this much memory to run. 
MAX_MEMORY=-Xmx7000m

#Choose a port to run on
PORT_NUMBER=5776

# CLASSPATH=fanseparser-0.2.2.jar
CLASSPATH=afansparser-0.2.jar
WORDNET=data/wordnet3/

SENTENCE_READER=tratz.parse.io.TokenizingSentenceReader
SENTENCE_WRITER=tratz.parse.io.DefaultSentenceWriter

POS_MODEL=posTaggingModel.gz
PARSE_MODEL=parseModel.gz

#POSSESSIVES_MODEL=""
#NOUN_COMPOUND_MODEL=""
#SRL_ARGS_MODELS=""
#SRL_PREDICATE_MODELS=""
#PREPOSITION_MODELS=""

POSSESSIVES_MODEL="-possmodel possessivesModel.gz"
NOUN_COMPOUND_MODEL="-nnmodel nnModel.gz"
SRL_ARGS_MODELS="-srlargsmodel srlArgsWrapper.gz"
SRL_PREDICATE_MODELS="-srlpredmodel srlPredWrapper.gz"
PREPOSITION_MODELS="-psdmodel psdModels.gz"

OUTPUT_ARG="$2"
INPUT_ARG="$1"

java $MAX_MEMORY -cp $CLASSPATH tratz.parse.SimpleParseClient ${PORT_NUMBER} ${INPUT_ARG} ${OUTPUT_ARG}
