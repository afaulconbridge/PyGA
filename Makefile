.PHONEY: test doc 

test:
	#run the test suite in test/
	#these also serve as examples
	
doc:
	#run sphinx to make documentation in doc/
	sphinx-build -b html -d doc/build/doctrees -D latex_paper_size=a4 doc/source doc
	sphinx-build -b latex -d doc/build/doctrees -D latex_paper_size=a4 doc/source doc
	
