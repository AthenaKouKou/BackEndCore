# common make vars and targets:
export API_DIR = "backendcore/api"
export COMMON_DIR = "backendcore/common"
export DATA_DIR = "backendcore/data"
export EMAIL_DIR = "backendcore/emailer"
export ENV_DIR = "backendcore/env"
export SEC_DIR = "backendcore/security"
export USER_DIR = "backendcore/users"

export PANDOC = pandoc
export PYLINT = flake8
export PYLINTFLAGS = --exclude=__main__.py

# make sure we test against local DB:
export LOCAL_MONGO=1

PYTHONFILES = $(shell ls *.py)
PYTESTFLAGS = -vv --verbose --cov-branch --cov-report term-missing --tb=short -W ignore::FutureWarning

MAIL_METHOD = api

FORCE:

tests: lint pytests

lint: $(patsubst %.py,%.pylint,$(PYTHONFILES))

%.pylint:
	$(PYLINT) $(PYLINTFLAGS) $*.py

pytests: FORCE
	echo $(USER_DB_FILE)
	export TEST_DB=1; pytest $(PYTESTFLAGS) --cov=$(PKG)

# test a python file:
%.py: FORCE
	$(PYLINT) $(PYLINTFLAGS) $@
	export TEST_DB=1; pytest $(PYTESTFLAGS) tests/test_$*.py

nocrud:
	-rm *~
	-rm *.log
	-rm *.out
	-rm .*swp
	-rm $(TESTDIR)/*~
