VENV=.venv
PACKAGE_NAME=RadarrStalledCleaner

ifeq ($(OS),Windows_NT)
    PYTHON=python
    CYAN=Cyan
    RED=Red
    RM=del /Q /F
    RMDIR=rd /s /q
    ACTIVATE=.\\$(VENV)\Scripts\activate.bat
    DEACTIVATE=.\\$(VENV)\Scripts\deactivate.bat
    LAUNCH_SCRIPT=.\\commands\launch_windows.bat
	VENV_SCRIPT=.\\commands\venv_windows.bat
	TEST_SCRIPT=.\\commands\test_windows.bat
	ECHO_SCRIPT=.\\commands\echo_color_windows.bat
else
    PYTHON=python
    CYAN=\033[96m
    RED=\033[91m
    RM=rm -f
    RMDIR=rm -rf
    ACTIVATE=source $(VENV)/bin/activate
    DEACTIVATE=deactivate
    LAUNCH_SCRIPT=.commands/launch_unix.sh
	VENV_SCRIPT=.commands/venv_unix.sh
	TEST_SCRIPT=.commands/test_unix.sh
	ECHO_SCRIPT=.commands/echo_color_unix.sh
endif

.PHONY clean:
clean:
	-@$(ECHO_SCRIPT) $(CYAN) "--------Cleaning the venv files--------"
	-$(RMDIR) $(VENV)
	-$(RMDIR) build
	-$(RMDIR) dist
	-@$(ECHO_SCRIPT) $(CYAN) "--------Finished cleaning the venv files--------"

.PHONY venv:
venv:
ifeq ($(OS),Windows_NT)
	@if not exist "$(VENV)" ( \
		@$(VENV_SCRIPT) \
	) else ( \
		@$(ECHO_SCRIPT) $(RED) "--------Venv already exists, if incorrect please use 'make clean-venv' and try again--------"; \
	)
else
	@if [ ! -d "$(VENV)" ]; then \
		@$(VENV_SCRIPT); \
	else \
		@$(ECHO_SCRIPT) $(RED) "--------Venv already exists, if incorrect please use 'make clean-venv' and try again--------"; \
	fi
endif

.PHONY launch:
launch: venv
	@$(ECHO_SCRIPT) $(CYAN) "--------Launching dev build--------"
	@$(LAUNCH_SCRIPT)

.PHONY test:
test: venv
	@$(ECHO_SCRIPT) $(CYAN) "--------Running tests--------"
	@$(TEST_SCRIPT)
