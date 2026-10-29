.PHONY: verify test
verify: test
	python3 agent.py evaluate --summary
	python3 scripts/check_docs.py
test:
	python3 -m unittest discover -s tests -v
	python3 scripts/report_model.py --check
