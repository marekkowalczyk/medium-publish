INSTALL_DIR ?= /usr/local/bin

.PHONY: install

install:
	chmod +x medium-publish
	ln -sf "$(PWD)/medium-publish" "$(INSTALL_DIR)/medium-publish"
	@echo "Installed to $(INSTALL_DIR)/medium-publish"
