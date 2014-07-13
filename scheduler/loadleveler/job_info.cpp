#include "job_info.hpp"
#include "common.hpp"
#include "exception.hpp"

#include <llapi.h>

#include <map>

typedef std::map<llapi::JobState, ::StepState> StateMap;

namespace llapi {
namespace {

//georg@TODO: use universal initialization
//Working around some g++-4.1 bug, that doesn't allow putting code inside namespace
//Maybe it's my bug, but I failed to find one
StateMap makeStateMap()
{
	StateMap result;
	result[Idle] = STATE_IDLE;
	result[Pending] = STATE_PENDING;
	result[Starting] = STATE_STARTING;
	result[Running] = STATE_RUNNING;
	result[CompletePending] = STATE_COMPLETE_PENDING;
	result[RejectPending] = STATE_REJECT_PENDING;
	result[RemovePending] = STATE_REMOVE_PENDING;
	result[VacatePending] = STATE_VACATE_PENDING;
	result[Completed] = STATE_COMPLETED;
	result[Rejected] = STATE_REJECTED;
	result[Removed] = STATE_REMOVED;
	result[Vacated] = STATE_VACATED;
	result[Canceled] = STATE_CANCELED;
	result[NotRun] = STATE_NOTRUN;
	result[Terminated] = STATE_TERMINATED;
	result[Unexpanded] = STATE_UNEXPANDED;
	result[SubmissionError] = STATE_SUBMISSION_ERR;
	result[Hold] = STATE_HOLD;
	result[Deferred] = STATE_DEFERRED;
	result[NotQueued] = STATE_NOTQUEUED;
	result[Preempted] = STATE_PREEMPTED;
	result[PreemptPending] = STATE_PREEMPT_PENDING;
	result[ResumePending] = STATE_RESUME_PENDING;
	return result;
}

StateMap JOB_STATE_MAP = makeStateMap();

} // anonymous namespace

JobsInfo::JobsInfo(JobState state)
{
	QueryHolder query(ll_query(JOBS), QueryDeleter());
	ll_set_request(query.get(), QUERY_ALL, NULL, ALL_DATA);

	REQUIRE(
		JOB_STATE_MAP.find(state) != JOB_STATE_MAP.end(),
		"Specified state isn't supported"
	);
	StepState llState = JOB_STATE_MAP[state];

	Element* job = getFirstObject(query, LL_SCHEDD, NULL);

	while (job != NULL)
	{
		Element* step = getData<Element*>(job, LL_JobGetFirstStep);

		while (step != NULL)
		{
			int stepState = getData<int>(step, LL_StepState);
			if (stepState == llState)
			{
				std::string name = getData<char*>(job, LL_JobName);
				std::string jobClass = getData<char*>(step, LL_StepJobClass);

				int cpusRequested = getData<int>(step, LL_StepBgSizeRequested);
				int cpusAllocated = getData<int>(step, LL_StepBgSizeAllocated);

				time_t submitTime = getData<time_t>(job, LL_JobSubmitTime);
				time_t dispatchTime = getData<time_t>(step, LL_StepDispatchTime);
				time_t startTime = getData<time_t>(step, LL_StepStartTime);
				time_t completionTime = getData<time_t>(step, LL_StepCompletionDate);

				/*
				 * georg@TODO: emplace_back
				 */
				JobInfo jobInfo(
					name,
					jobClass,
					state,
					cpusRequested,
					cpusAllocated,
					submitTime,
					dispatchTime,
					startTime,
					completionTime
				);
				jobInfos_.push_back(jobInfo);
			}

			step = getData<Element*>(job, LL_JobGetNextStep);
		}

		job = getNextObject(query.get());
	}
}

} //namespace llapi
