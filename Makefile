package: doc
	rm VDL-release.zip
	-find . -name "*.pyc" | xargs rm
	zip -r VDL-release.zip *

doc:
	sphinx-build ./docs ./html
