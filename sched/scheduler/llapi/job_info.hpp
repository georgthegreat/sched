#pragma once

#include "common.hpp"

#include <ctime>
#include <string>
#include <set>
#include <vector>

namespace llapi {

enum StepState
{
	Idle,
	Pending,
	Starting,
	Running,
	CompletePending,
	RejectPending,
	RemovePending,
	VacatePending,
	Completed,
	Rejected,
	Removed,
	Vacated,
	Canceled,
	NotRun,
	Terminated,
	Unexpanded,
	SubmissionError,
	Hold,
	Deferred,
	NotQueued,
	Preempted,
	PreemptPending,
	ResumePending
};

class JobInfo
{
public:
	JobInfo(
		const std::string& jobId,
		const std::string& stepId,
		const std::string& stepClass,
		StepState stepState,
		size_t cpusRequested,
		size_t cpusAllocated,
		time_t submitTime,
		time_t dispatchTime,
		time_t startTime,
		time_t completionTime
	) :
		jobId_(jobId),
		stepId_(stepId),
		stepClass_(stepClass),
		stepState_(stepState),
		cpusRequested_(cpusRequested),
		cpusAllocated_(cpusAllocated),
		submitTime_(submitTime),
		dispatchTime_(dispatchTime),
		startTime_(startTime),
		completionTime_(completionTime)
	{
	}

	const std::string& jobId() const
	{
		return jobId_;
	}

	const std::string& stepId() const
	{
		return stepId_;
	}

	const std::string& stepClass() const
	{
		return stepClass_;
	}

	StepState stepState() const
	{
		return stepState_;
	}

	size_t cpusRequested() const
	{
		return cpusRequested_;
	}

	size_t cpusAllocated() const
	{
		return cpusAllocated_;
	}

	time_t submitTime() const
	{
		return submitTime_;
	}

	time_t dispatchTime() const
	{
		return dispatchTime_;
	}

	time_t startTime() const
	{
		return startTime_;
	}

	time_t completionTime() const
	{
		return completionTime_;
	}

private:
	std::string jobId_;
	std::string stepId_;
	std::string stepClass_;

	StepState stepState_;

	size_t cpusRequested_;
	size_t cpusAllocated_;

	time_t submitTime_;
	time_t dispatchTime_;
	time_t startTime_;
	time_t completionTime_;
};

class JobsInfo
{
public:
	JobsInfo(StepState state);
	JobsInfo(const std::set<StepState>& states);
	JobsInfo(const std::string& jobId);

	typedef std::vector<JobInfo> JobInfos;
	typedef JobInfos::iterator iterator;
	typedef JobInfos::const_iterator const_iterator;

	iterator begin()
	{
		return jobInfos_.begin();
	}

	iterator end()
	{
		return jobInfos_.end();
	}

	size_t size() const
	{
		return jobInfos_.size();
	}

	const JobInfo& operator[] (size_t index) const
	{
		return jobInfos_[index];
	}

private:
	JobInfos extractJobInfos(Element* llJob);
	JobInfos jobInfos_;
};

} //namespace llapi
