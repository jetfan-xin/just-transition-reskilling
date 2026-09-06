.PHONY: verify figures

verify:
	python3 -B scripts/verify.py
	python3 -B scripts/build_figures.py --check
	python3 -B scripts/check_public_release.py

figures:
	python3 -B scripts/build_figures.py
