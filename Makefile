SHELL = /bin/bash
PYTHON = python3
PIP = pip3

define HELP
cat <<EOF
ocrd_repair_inconsistencies

Targets:
	deps     Install Python dependencies via pip
	install  Install Python package
EOF
endef
export HELP
help: ; @eval "$$HELP"

deps:
	$(PIP) install -r requirements.txt

install:
	$(PIP) install .
