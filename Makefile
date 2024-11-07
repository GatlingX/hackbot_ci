

doc-install:
	cd docs && npm install && cd ..

doc-dev: doc-install
	cd docs && npm run dev & cd ..


doc:
	cd documentation && npm start && cd ..


