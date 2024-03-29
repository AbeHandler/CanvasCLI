.PHONY: bump
bump:
	cz bump

.PHONY: changelog
changelog:
	cz changelog

.PHONY: conda
conda:
	conda env update --file config/canvascli.yml --prune -n canvascli

.PHONY: initconda
initconda:
	conda env create -f config/canvascli.yml