.PHONY: reports

reports:
	@cd scripts && python adoption_search_code.py $(TOKEN) > results/adoption_search_code.txt
