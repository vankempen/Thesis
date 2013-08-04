output/Thesis.pdf : Thesis.tex output/Thesis.bbl
	pdflatex -output-directory output Thesis
	pdflatex -output-directory output Thesis
output/Thesis.bbl : Thesis.tex output/Thesis.aux ThesisBiblio.bib
	bibtex output/Thesis.aux
output/Thesis.aux : Thesis.tex
	pdflatex -output-directory output Thesis