PYVERSION = 3.4m
CPPFLAGS += -m64 -I/opt/ibmll/LoadL/full/include -I$(CHROOT)/usr/include/python$(PYVERSION) -Wall
LDFLAGS += \
	-m64 \
	-lllapi \
	-lboost_python \
	-lboost_regex \
	-lboost_system \
	-lboost_thread \
	-lpython$(PYVERSION) \

LIB = _llapi.so
CXX = g++

MODS = \
	common.cpp \
	pymod.cpp \
	job_info.cpp \
	job_submit.cpp \
	machine_info.cpp \

OBJS = $(MODS:.cpp=.o)

all: $(LIB);

$(LIB): $(OBJS)
	$(CXX) $(LDFLAGS) -shared $^ -o $@

%.o: %.cpp
	$(CXX) $(CPPFLAGS) -c $<

deps.mk: $(MODS)
	$(CXX) $(CPPFLAGS) -MM $^ > $@

ifneq ($(MAKECMDGOALS), clean)
ifneq ($(MAKECMDGOALS), distclean)
-include deps.mk
endif
endif

clean:
	rm -rf *.o *.core parser deps.mk

distclean: clean
	rm -rf $(LIB)

