.PHONY: reports

reports:
	@[ -d results ] || mkdir results
	@python adoption_search_code.py $(TOKEN) > results/adoption_search_code.txt
