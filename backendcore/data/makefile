export PKG = backendcore.data
export FORCE_MEM = 1
include ../../common.mk

tests: lint pytests
	cd databases; make tests
