#pragma once

#include <ctime>
#include <string>
#include <vector>

namespace llapi {

enum JobState
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
		const std::string& name,
		const std::string& jobClass,
		JobState state,
		size_t cpusRequested,
		size_t cpusAllocated,
		time_t submitTime,
		time_t dispatchTime,
		time_t startTime,
		time_t completionTime
	) :
		name_(name),
		jobClass_(jobClass),
		state_(state),
		cpusRequested_(cpusRequested),
		cpusAllocated_(cpusAllocated),
		submitTime_(submitTime),
		dispatchTime_(dispatchTime),
		startTime_(startTime),
		completionTime_(completionTime)
	{
	}

	const std::string& name() const
	{
		return name_;
	}

	const std::string& jobClass() const
	{
		return jobClass_;
	}

	JobState state() const
	{
		return state_;
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
	std::string name_;
	std::string jobClass_;

	JobState state_;

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
	JobsInfo(JobState state);

	typedef std::vector<JobInfo>::iterator iterator;
	typedef std::vector<JobInfo>::const_iterator const_iterator;

	iterator begin()
	{
		return jobInfos_.begin();
	}

	iterator end()
	{
		return jobInfos_.end();
	}

	const_iterator begin() const
	{
		return jobInfos_.begin();
	}

	const_iterator end() const
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
	std::vector<JobInfo> jobInfos_;
};

} //namespace llapi
