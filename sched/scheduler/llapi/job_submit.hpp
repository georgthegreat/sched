#pragma once

#include "common.hpp"
#include "exception.hpp"
#include "job_info.hpp"

#include <llapi.h>

#include <boost/shared_ptr.hpp>
#include <boost/thread/mutex.hpp>

#include <cstddef>
#include <fstream>
#include <set>
#include <string>
#include <vector>

namespace llapi {

class JobMonitor;

class SubmitInfo
{
public:
	SubmitInfo(
		const std::vector<std::string>& command,
		const std::string& outputStream,
		const std::string& errorStream,
		size_t nodesLimit,
		size_t timeLimitSeconds
	) :
		command_(command),
		outputStream_(outputStream),
		errorStream_(errorStream),
		nodesLimit_(nodesLimit),
		timeLimitSeconds_(timeLimitSeconds)
	{
		REQUIRE(
			!command_.empty(),
			"Command can't be empty"
		);
	}

	virtual ~SubmitInfo()
	{
	}

private:
	std::vector<std::string> command_;

	std::string outputStream_;
	std::string errorStream_;
	
	size_t nodesLimit_;
	size_t timeLimitSeconds_;

	friend class JobMonitor;
	//Should be called via JobMonitor
	//submit job to LoadLeveler, returns job name
	std::string submit(
		const std::string& monitorProgram,
		const std::string& monitorArgs
	) const;
};

struct WaitResult
{
public:
	WaitResult(
		const std::string& jobId,
		llapi::StepState stepState
	) :
		jobId_(jobId),
		stepState_(stepState)
	{
	}

	const std::string& jobId() const
	{
		return jobId_;
	}

	llapi::StepState stepState() const
	{
		return stepState_;
	}

private:
	std::string jobId_;
	llapi::StepState stepState_;
};

class JobMonitor
{
public:
	/*
	 * Expects folder with _llapi.so in workingDir folder
	 */
	JobMonitor(
		const std::string& workingDir
	);

    //Submits job to LoadLeveler, returns submitted job id
	std::string submitJob(const SubmitInfo& submitInfo);

	/* Blocks current thread until
	 * any of previously submitted jobs will be
	 * marked as finished or failed
	 */
	WaitResult wait();

private:
	std::string monitorProgram_;
	TemporaryFile monitorLog_;
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
