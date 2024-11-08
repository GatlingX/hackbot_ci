
VERSION=0.1.0



doc-install:
	cd docs && npm install && cd ..

doc-dev: doc-install
	cd docs && npm run dev & cd ..


doc:
	cd documentation && npm start && cd ..




deploy:
	cd documentation && npm run build && cd ..

# Deployment guide: https://docusaurus.io/docs/deployment


build:
	cd documentation && npm run build && cd ..
	cd documentation && zip -r build.zip build/ && cd ..
	open documentation



