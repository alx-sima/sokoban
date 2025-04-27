ARCHIVE=Alexandru_Sima_332CA_Tema1IA

doc: documentation/Sokoban.tex images/*
	make -C documentation

pack: $(ARCHIVE).zip

$(ARCHIVE).zip:
	zip -FSr $(ARCHIVE).zip documentation/Sokoban.{tex,pdf} images/* \
	search_methods/*.py sokoban/*.py solutions/**/*.gif tests/*.yaml \
	main.ipynb requirements.txt

clean:
	make -C documentation clean
	rm -f $(ARCHIVE).zip
	rm -rf **/__pycache__/
