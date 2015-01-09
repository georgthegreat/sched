#pragma once

#include <cstddef>
#include <stdexcept>
#include <string>
#include <sstream>

namespace llapi
{

const int ERROR_NO_VALID_OBJECTS = -6;

class Exception : public std::exception
{
public:
	Exception(const std::string& msg)
		: msg_(msg)
	{
	}

	virtual const char* what() const throw()
	{
		return msg_.c_str();
	}

	virtual ~Exception() throw()
	{
	}
private:
	std::string msg_;
};

/**
 * Class representing integer code errors received from ll_get_objs call
 */
class GetObjectsException : public std::exception
{
public:
	GetObjectsException(int errorCode) :
		errorCode_(errorCode)
	{
	}

	virtual const char* what() const throw()
	{
		switch (errorCode_)
		{
			case -1:
				return "query_element isn't valid";

			case -2:
				return "query_daemon isn't valid";

			case -3:
				return "Can't resolve hostname";

			case -4:
				return "Request type for specified daemon isn't valid";

			case -5:
				return "System error";

			case ERROR_NO_VALID_OBJECTS:
				return "No valid objects meet the request";

			case -7:
				return "Configuration error";

			case -9:
				return "Connection to daemon failed";

			case -10:
				return "Error processing history file";

			case -11:
				return "History file must be specified in hostname argument";

			case -12:
				return "Unable to access history file";

			default:
				return "Unknown error";
		}
	}

	virtual ~GetObjectsException() throw()
	{
	}

	int errorCode() const
	{
		return errorCode_;
	}

private:
	int errorCode_;
};

class GetDataException : public std::exception
{
public:
	GetDataException(int errorCode) :
		errorCode_(errorCode)
	{
	}

	virtual const char* what() const throw()
	{
		switch (errorCode_)
		{
			case -1:
				return "Object isn't valid";

			case -2:
				return "Data specification isn't valid";

			default:
				return "Unknown error";
		}
	}

	virtual ~GetDataException() throw()
	{
	}
private:
	int errorCode_;
};

#define REQUIRE(expression, message) \
	if	(!(expression)) \
	{ \
		std::stringstream ss; \
		ss << message; \
		throw Exception(ss.str()); \
	} \

} //namespace llapi
