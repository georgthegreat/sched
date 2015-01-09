#include "job_info.hpp"
#include "common.hpp"
#include "exception.hpp"

#include <llapi.h>

#include <algorithm>
#include <map>

namespace llapi {
namespace {

typedef std::map<int, llapi::StepState> StateMap;

//georg@TODO: use universal initialization
//Working around some g++-4.1 bug, that doesn't allow putting code inside namespace
//Maybe it's my bug, but I've failed to find one
StateMap makeStateMap()
{
	StateMap result;
	result[STATE_IDLE] = Idle;
	result[STATE_PENDING] = Pending;
	result[STATE_STARTING] = Starting;
	result[STATE_RUNNING] = Running;
	result[STATE_COMPLETE_PENDING] = CompletePending;
	result[STATE_REJECT_PENDING] = RejectPending;
	result[STATE_REMOVE_PENDING] = RemovePending;
	result[STATE_VACATE_PENDING] = VacatePending;
	result[STATE_COMPLETED] = Completed;
	result[STATE_REJECTED] = Rejected;
	result[STATE_REMOVED] = Removed;
	result[STATE_VACATED] = Vacated;
	result[STATE_CANCELED] = Canceled;
	result[STATE_NOTRUN] = NotRun;
	result[STATE_TERMINATED] = Terminated;
	result[STATE_UNEXPANDED] = Unexpanded;
	result[STATE_SUBMISSION_ERR] = SubmissionError;
	result[STATE_HOLD] = Hold;
	result[STATE_DEFERRED] = Deferred;
	result[STATE_NOTQUEUED] = NotQueued;
	result[STATE_PREEMPTED] = Preempted;
	result[STATE_PREEMPT_PENDING] = PreemptPending;
	result[STATE_RESUME_PENDING] = ResumePending;
	return result;
}

StateMap JOB_STATE_MAP = makeStateMap();

class StepStateFilter
{
public:
	StepStateFilter(StepState stepState) :
		stepState_(stepState)
	{
	}

	bool operator() (const JobInfo& jobInfo)
	{
		return (jobInfo.stepState() == stepState_);
	}

private:
	StepState stepState_;
};

class StepStateSetFilter
{
public:
	StepStateSetFilter(const std::set<StepState>& stepStates) :
		stepStates_(stepStates)
	{
	}

	bool operator() (const JobInfo& jobInfo)
	{
		return (stepStates_.find(jobInfo.stepState()) != stepStates_.end());
	}

private:
	std::set<StepState> stepStates_;
};

class JobIdFilter
{
public:
	JobIdFilter(const std::string& jobId) :
		jobId_(jobId)
	{
	}

	bool operator() (const JobInfo& jobInfo)
	{
		return (jobInfo.jobId() == jobId_);
	}

private:
	std::string jobId_;
};


} // anonymous namespace

JobsInfo::JobInfos JobsInfo::extractJobInfos(Element* llJob)
{
	JobInfos result;

	std::string jobId = getData<char*>(llJob, LL_JobName);

	Element* step = getData<Element*>(llJob, LL_JobGetFirstStep);
	while (step != NULL)
	{
		StepState stepState = JOB_STATE_MAP[getData<int>(step, LL_StepState)];

		std::string stepId = getData<char*>(step, LL_StepID);
		std::string stepClass = getData<char*>(step, LL_StepJobClass);

		int cpusRequested = getData<int>(step, LL_StepBgSizeRequested);
		int cpusAllocated = getData<int>(step, LL_StepBgSizeAllocated);

		time_t submitTime = getData<time_t>(llJob, LL_JobSubmitTime);
		time_t dispatchTime = getData<time_t>(step, LL_StepDispatchTime);
		time_t startTime = getData<time_t>(step, LL_StepStartTime);
		time_t completionTime = getData<time_t>(step, LL_StepCompletionDate);

		/*
		 * georg@TODO: emplace_back
		 */
		JobInfo jobInfo(
			jobId,
			stepId,
			stepClass,
			stepState,
			cpusRequested,
			cpusAllocated,
			submitTime,
			dispatchTime,
			startTime,
			completionTime
		);
		result.push_back(jobInfo);

		step = getData<Element*>(llJob, LL_JobGetNextStep);
	}

	return result;
}

JobsInfo::JobsInfo(StepState stepState)
{
	QueryHolder query(ll_query(JOBS), QueryDeleter());
	ll_set_request(query.get(), QUERY_ALL, NULL, ALL_DATA);

	Element* job = NULL;
	try
	{
		job = getFirstObject(query, LL_SCHEDD, NULL);
	}
	catch (const GetObjectsException& ex)
	{
		if (ex.errorCode() == ERROR_NO_VALID_OBJECTS)
		{
			return;
		}
		else
		{
			throw;
		}
	}

	while (job != NULL)
	{
		const JobInfos& jobInfos = extractJobInfos(job);

		StepStateFilter filter(stepState);
		for (
			JobInfos::const_iterator it = jobInfos.begin();
			it != jobInfos.end();
			++it
		)
		{
			if (filter(*it))
			{
				jobInfos_.push_back(*it);
			}
		}

		job = getNextObject(query.get());
	}
}


JobsInfo::JobsInfo(const std::string& jobId)
{
	QueryHolder query(ll_query(JOBS), QueryDeleter());
	ll_set_request(query.get(), QUERY_ALL, NULL, ALL_DATA);

	Element* job = NULL;
	try
	{
		job = getFirstObject(query, LL_SCHEDD, NULL);
	}
	catch (const GetObjectsException& ex)
	{
		if (ex.errorCode() == ERROR_NO_VALID_OBJECTS)
		{
			return;
		}
		else
		{
			throw;
		}
	}

	while (job != NULL)
	{
		const JobInfos& jobInfos = extractJobInfos(job);

		JobIdFilter filter(jobId);
		for (
			JobInfos::const_iterator it = jobInfos.begin();
			it != jobInfos.end();
			++it
		)
		{
			if (filter(*it))
			{
				jobInfos_.push_back(*it);
			}
		}

		job = getNextObject(query.get());
	}
}


JobsInfo::JobsInfo(const std::set<StepState>& stepStates)
{
	QueryHolder query(ll_query(JOBS), QueryDeleter());
	ll_set_request(query.get(), QUERY_ALL, NULL, ALL_DATA);

	Element* job = NULL;
	try
	{
		job = getFirstObject(query, LL_SCHEDD, NULL);
	}
	catch (const GetObjectsException& ex)
	{
		if (ex.errorCode() == ERROR_NO_VALID_OBJECTS)
		{
			return;
		}
		else
		{
			throw;
		}
	}

	while (job != NULL)
	{
		const JobInfos& jobInfos = extractJobInfos(job);

		StepStateSetFilter filter(stepStates);
		for (
			JobInfos::const_iterator it = jobInfos.begin();
			it != jobInfos.end();
			++it
		)
		{
			if (filter(*it))
			{
				jobInfos_.push_back(*it);
			}
		}

		job = getNextObject(query.get());
	}
}

} //namespace llapi

