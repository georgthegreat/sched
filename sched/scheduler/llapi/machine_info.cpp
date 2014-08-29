#include "machine_info.hpp"
#include "common.hpp"

#include <llapi.h>

#include <iostream>

namespace llapi {

MachineInfo::MachineInfo() :
	totalNodes_(0)
{
	QueryHolder query(ll_query(BLUE_GENE), QueryDeleter());
	ll_set_request(query.get(), QUERY_ALL, NULL, ALL_DATA);

	Element* machine = getFirstObject(query, LL_CM, NULL);

	if (machine != NULL)
	{
		//Blue Gene has three-dimensional topology
		int* baseDims = getData<int*>(machine, LL_BgMachineBPSize);
		size_t basePartitionsSize = baseDims[0] * baseDims[1] * baseDims[2];

		int* partDims = getData<int*>(machine, LL_BgMachineSize);
		size_t basePartitionsCount = partDims[0] * partDims[1] * partDims[2];

		totalNodes_ = basePartitionsSize * basePartitionsCount;

	}
}

} //namespace llapi
