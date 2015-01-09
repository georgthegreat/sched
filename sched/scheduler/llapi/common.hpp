#pragma once

#include "exception.hpp"

#include <llapi.h>

#include <boost/noncopyable.hpp>
#include <boost/shared_ptr.hpp>

#include <Python.h>

namespace llapi {

typedef LL_element Element;

/*
 * Utility class releasing Python GIL in ctor, releasing it in dtor
 */
class PythonThreadSaver
{
public:
	PythonThreadSaver()
	{
		threadState_ = PyEval_SaveThread();
	}

	~PythonThreadSaver()
	{
		PyEval_RestoreThread(threadState_);
	}

private:
	PyThreadState* threadState_;

};

class QueryDeleter
{
public:
	void operator() (Element* query)
	{
		ll_free_objs(query);
		ll_deallocate(query);
	}
};

/*
 * georg@TODO: use std::unique_ptr here
 */
typedef boost::shared_ptr<Element> QueryHolder;

//===== Functions =====

/*
 * ll_get_objs proxy, throwing in case of error.
 * Doesn't have objectNumber element, since it looks particularly useless
 */
Element* getFirstObject(
	QueryHolder& holder,
	LL_Daemon daemon,
	const char* hostname
);

Element* getNextObject(
	Element* element
);

template<typename T>
T getData(Element* element, LLAPI_Specification spec)
{
	int errorCode = 0;
	T result;
	errorCode = ll_get_data(element, spec, &result);
	if (errorCode != 0)
	{
		throw GetDataException(errorCode);
	}
	return result;
}

//named temporary file that will be automatically removed upon object destruction
class TemporaryFile : boost::noncopyable
{
public:
	TemporaryFile(const std::string& prefix);

	virtual ~TemporaryFile();

	const std::string& name() const
	{
		return name_;
	}

	static std::string randomName(const std::string& prefix, size_t length);

private:
	std::string name_;
};


} //namespace llapi
