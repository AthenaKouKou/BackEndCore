# common make vars and targets:
export CODE_ROOT = "backendcore"
export API_DIR = "$(CODE_ROOT)/api"
export COMMON_DIR = "$(CODE_ROOT)/common"
export DATA_DIR = "$(CODE_ROOT)/data"
export EMAIL_DIR = "$(CODE_ROOT)/emailer"
export ENV_DIR = "$(CODE_ROOT)/env"
export SEC_DIR = "$(CODE_ROOT)/security"
export TEMPL_DIR = "$(CODE_ROOT)/templates"
export USER_DIR = "$(CODE_ROOT)/users"

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
