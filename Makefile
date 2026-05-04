.PHONY: reports report

DB_FLAG    = $(if $(DB),--db $(DB))
NOTES_FLAG = $(if $(NOTES),--notes "$(NOTES)")

reports:
	@cd scripts && python adoption_search_code.py $(TOKEN) $(DB_FLAG) $(NOTES_FLAG) > results/adoption_search_code.txt
	@cd scripts && python adoption_search_fe_plugins_code.py $(TOKEN) $(DB_FLAG) $(NOTES_FLAG) > results/adoption_search_fe_plugins_code.txt

report:
	@cd scripts && python generate_report.py --db $(DB) --out results/report.md
