PYTHON ?= python3
PREFIX ?= $(HOME)/.local
.PHONY: build test install package
build:
	$(PYTHON) tools/timeoutctl.py build
test:
	$(PYTHON) tools/timeoutctl.py test
install:
	$(PYTHON) tools/timeoutctl.py install --prefix "$(PREFIX)"
package:
	$(PYTHON) tools/timeoutctl.py package
