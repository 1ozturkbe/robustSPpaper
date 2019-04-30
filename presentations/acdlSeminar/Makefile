# Aero Astro template
# Max Opgenoord
# August 2017

MAIN = main

default:
	pdflatex $(MAIN).tex

all:
	pdflatex $(MAIN).tex
	biber $(MAIN)
	pdflatex $(MAIN).tex
	pdflatex $(MAIN).tex

clean:
	mv $(MAIN).tex temp.tex
	mv $(MAIN).pdf temp.pdf
	rm $(MAIN)*
	mv temp.tex $(MAIN).tex
	mv temp.pdf $(MAIN).pdf
