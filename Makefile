# ----------------------------
# Configuration
# ----------------------------

PANDOC      := pandoc
PDF_ENGINE  := xelatex

SEMESTER		:= Sp26
SRC         := $(SEMESTER).md
OUTDIR      := build
OUTPDF      := $(OUTDIR)/$(SEMESTER)_Coursework_Forecast.pdf
OUTTEX      := $(OUTDIR)/$(SEMESTER)_Coursework_Forecast.tex

HEADERS     := \
	headers/highlight.tex \
	headers/checkboxes.tex

FILTERS     := \
	filters/columns.lua \
	filters/checkboxes.lua \
	filters/highlight.lua

# Convert filters to repeated flags
HEADER_FLAGS:= $(foreach f,$(HEADERS),--include-in-header=$(f))
LUA_FLAGS   := $(foreach f,$(FILTERS),--lua-filter=$(f))

# ----------------------------
# Targets
# ----------------------------

.PHONY: all pdf tex clean ast

all: pdf

pdf: $(OUTPDF)
tex: $(OUTTEX)

$(OUTTEX): $(SRC) $(HEADERS) $(FILTERS) | $(OUTDIR)
	$(PANDOC) $(SRC) \
		$(HEADER_FLAGS) \
		$(LUA_FLAGS) \
		-o $@

$(OUTPDF): $(SRC) $(HEADERS) $(FILTERS) | $(OUTDIR)
	$(PANDOC) $(SRC) \
		--pdf-engine=$(PDF_ENGINE) \
		$(HEADER_FLAGS) \
		$(LUA_FLAGS) \
		-o $@
	mv $(OUTPDF) ${HOME}/iCloud/Documents


$(OUTDIR):
	mkdir -p $(OUTDIR)


clean:
	rm -rf $(OUTDIR)

# Debug: inspect Pandoc AST
ast:
	$(PANDOC) $(SRC) -t native | less

