

doc-install:
	cd docs && npm install && cd ..

doc-dev: doc-install
	cd docs && npm run dev & cd ..


doc:
	cd documentation && npm start && cd ..




deploy:
	cd documentation && npm run build && cd ..

# Deployment guide: https://docusaurus.io/docs/deployment





