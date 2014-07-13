CXX = mpicxx
CXXFLAGS = -Wall

DATA_LARGE = $(wildcard data.4gb.*)
DATA_SMALL = data.256mb.in.aa #$(wildcard data.256mb.*)

NODES_SMALL = 32
NODES_LARGE = 1024

SRCS = bg_mpi_test.cpp
BIN = bg_mpi_test

$(BIN): $(SRCS)
	$(CXX) $(CXXFLAGS) $^ -o $@

submit_large: $(BIN)
	for FILE in $(DATA_LARGE); \
	do \
		mpisubmit.bg \
			-n $(NODES_LARGE) \
			-w 00:03:00 \
			-m vn \
			--stdout log/$^.'$$(jobid)'.out \
			--stderr log/$^.'$$(jobid)'.err \
			--debug \
			$< -- $$FILE $$FILE.out; \
	done

submit_small: $(BIN)
	for FILE in $(DATA_SMALL); \
	do \
		mpisubmit.bg \
			-n $(NODES_SMALL) \
			-w 00:03:00 \
			-m vn \
			--stdout log/$^.'$$(jobid)'.out \
			--stderr log/$^.'$$(jobid)'.err \
			--debug \
			$< -- $$FILE $$FILE.out; \
	done

distclean:
	rm -f $(BIN)
