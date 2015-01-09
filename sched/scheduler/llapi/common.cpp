#include "common.hpp"

#include <cstdio>
#include <cstddef>
#include <fstream>

namespace llapi {

namespace {

const std::string NAME_CHARS =
	"abcdefghijklmnopqrstuvwxyz"
	"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	"0123456789";

const size_t NAME_SIZE = 20;

} //anonymous namespace

Element* getFirstObject(
    QueryHolder& holder,
    LL_Daemon daemon,
    const char* hostname
)
{
    int errorCode = 0;
    int objectNumber = 0;
    Element* result = ll_get_objs(
        holder.get(), daemon, const_cast<char*>(hostname), &objectNumber, &errorCode
    );
    if (errorCode != 0)
    {
        throw GetObjectsException(errorCode);
    }
    return result;
}

Element* getNextObject(
    Element* element
)
{
    return ll_next_obj(element);
}

TemporaryFile::TemporaryFile(const std::string& prefix)
{
	while (true)
	{
		name_ = randomName(prefix, NAME_SIZE);
		if (!std::ifstream(name_.c_str()).good()) {
			break;
		}
	}
}

TemporaryFile::~TemporaryFile()
{
	remove(name_.c_str());
}

std::string TemporaryFile::randomName(const std::string& prefix, size_t length)
{
	size_t nameCharsSize = NAME_CHARS.size();

	std::string result = prefix;
	for (size_t i = 0; i < length; ++i)
	{
		size_t index = (static_cast<size_t>(std::rand()) * nameCharsSize) / RAND_MAX;
		result += NAME_CHARS[index];
	}

	return result;
}

} //namespace llapi
