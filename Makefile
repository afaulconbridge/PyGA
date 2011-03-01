.PHONEY: test doc 

test:
	#run the test suite in test/
	#these also serve as examples
	
docs:
	#run sphinx to make documentation in doc/
	#NOTE: name of command is docs not doc. Make does not like phoney commands
	#with the same name as the file...
	sphinx-build -b html -d doc/build/doctrees doc/source doc/html
	sphinx-build -b latex -d doc/build/doctrees -D latex_paper_size=a4 doc/source doc/latex
	#pdflatex is invoced via this shell script
	#so that paths are local and its run repeatedly
	doc/latex/runlatex.sh
	
