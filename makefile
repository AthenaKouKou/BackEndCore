# Make sure you have KOUKOU_HOME set before running this.
include common.mk

WEB_BUILD_PUBLIC_URL ?= /static/react

all_tests: FORCE
	cd $(API_DIR); make tests
	cd $(COMMON_DIR); make tests
	cd $(DATA_DIR); make tests
	cd $(EMAIL_DIR); make tests
	cd $(ENV_DIR); make tests
	cd $(SEC_DIR); make tests
	cd $(USER_DIR); make tests

tests: FORCE
	echo "Run make all_tests from top level dir."

docs: $(PYTHONFILES)
	rm -rf $(HTML_DOCS_DIR)
	pydoc3 -f --html -o $(DOCS_DIR) -c show_source_code=False --skip-errors $(AQL_DIR) $(API_SERVER_DIR) $(LIB_DIR) $(SCRIPTS_DIR)

github:
	-git commit -a
	git push origin main

# GitHub Actions deploys the staging branch for us.
staging: all_tests github

prod: all_tests github

dev_env:
	pip3 install --upgrade pip
	pip3 install -r requirements-dev.txt
