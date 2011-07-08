.PHONEY: test doc help

help:
	@echo "The following targets are accepted:"
	@echo "    help     Display this help message"
	@echo "    docs     Generate documentation"
	@echo "    test     Run the test/example suite"

test:
	#run the test suite in test/
	#these also serve as examples
	
docs:
	#run sphinx to make documentation in doc/
	#NOTE: name of command is docs not doc. Make does not like phoney commands
	#with the same name as the file...
	sphinx-build -b html -d doc/build/doctrees doc/source doc/html
	sphinx-build -b latex -d doc/build/doctrees -D latex_paper_size=a4 doc/source doc/latex
	cd doc/latex; pdflatex PyGA > /dev/null; \
	              pdflatex PyGA > /dev/null; \
	              pdflatex PyGA > /dev/null
	
develop:
	sudo python setup.py develop
	sudo rm -rf PyGA.egg-info/
