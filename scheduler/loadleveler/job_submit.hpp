#pragma once

#include "exception.hpp"

#include <llapi.h>

#include <boost/shared_ptr.hpp>

#include <string>
#include <vector>

namespace llapi {

class SubmitInfo
{
public:
	SubmitInfo(
		const std::vector<std::string>& command,
		const std::string outputStream,
		const std::string errorStream,
		const std::string jobClass
	) :
		command_(command),
		outputStream_(outputStream),
		errorStream_(errorStream),
		jobClass_(jobClass)
	{
		REQUIRE(
			!command_.empty(),
			"Command can't be empty"
		);
	}

	virtual ~SubmitInfo()
	{
	}

	//submit job to LoadLeveler, returns job name
	std::string submit();

private:
	std::vector<std::string> command_;

	std::string outputStream_;
	std::string errorStream_;

	std::string jobClass_;
};

typedef LL_job SubmittedJob;
typedef boost::shared_ptr<SubmittedJob> SubmittedJobHolder;

class SubmittedJobDeleter
{
public:
	void operator() (SubmittedJob* job)
	{
		llfree_job_info(job, LL_JOB_VERSION);
		delete job;
	}
};

} //namespace llapi
