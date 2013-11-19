Output/Thesis.pdf : Thesis.tex Output/Thesis.bbl
	pdflatex -output-directory Output Thesis
	pdflatex -output-directory Output Thesis
Output/Thesis.bbl : Thesis.tex Output/Thesis.aux ThesisBiblio.bib
	bibtex Output/Thesis.aux
Output/Thesis.aux : Thesis.tex
	pdflatex -output-directory Output Thesis
