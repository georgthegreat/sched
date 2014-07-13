#pragma once

#include "common.hpp"

#include <cstddef>

namespace llapi {

class MachineInfo
{
public:
	MachineInfo();

	size_t totalNodes() const
	{
		return totalNodes_;
	}

private:
	size_t totalNodes_;
};

}
