
.PHONY: install
install:
	sudo pip3 install -r requirements.txt

.PHONY: run
run:
	python3 questionnaire.py

.PHONY: test
test:
	python3 questionnaire.py --test
