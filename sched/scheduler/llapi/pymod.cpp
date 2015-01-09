#include "job_info.hpp"
#include "job_submit.hpp"
#include "machine_info.hpp"

#include <boost/noncopyable.hpp>
#include <boost/python.hpp>
#include <boost/shared_ptr.hpp>

#include <cstdlib>
#include <ctime>
#include <string>
#include <vector>

namespace llapi {

boost::shared_ptr<SubmitInfo> makeSubmitInfo(
	const boost::python::list& command,
	const std::string& outputStream,
	const std::string& errorStream,
	size_t nodesLimit,
	size_t timeLimitSeconds
)
{
	std::vector<std::string> commandVector;
	for (int i = 0; i < len(command); ++i)
	{
		std::string arg = boost::python::extract<std::string>(command[i]);
		commandVector.push_back(arg);
	}

	return boost::shared_ptr<SubmitInfo>(new SubmitInfo(
		commandVector,
		outputStream,
		errorStream,
		nodesLimit,
		timeLimitSeconds
	));
}

boost::shared_ptr<JobsInfo> makeJobsInfoFromStepState(llapi::StepState state)
{
	return boost::shared_ptr<JobsInfo>(new JobsInfo(state));
}

boost::shared_ptr<JobsInfo> makeJobsInfoFromJobId(const std::string& jobId)
{
	return boost::shared_ptr<JobsInfo>(new JobsInfo(jobId));
}

boost::shared_ptr<JobsInfo> makeJobsInfoFromList(const boost::python::list& list)
{
	std::set<StepState> stepStates;
	for (int i = 0; i < len(list); ++i) {
		StepState state = boost::python::extract<StepState>(list[i]);
		stepStates.insert(state);
	}

	return boost::shared_ptr<JobsInfo>(new JobsInfo(stepStates));
}

}

BOOST_PYTHON_MODULE(_llapi)
{
	using namespace boost::python;
	using namespace llapi;
	srand(time(NULL));

	enum_<llapi::StepState>("StepState")
		.value("Idle", Idle)
		.value("Pending", Pending)
		.value("Starting", Starting)
 	   	.value("Running", Running)
		.value("CompletePending", CompletePending)
		.value("RejectPending", RejectPending)
		.value("RemovePending", RemovePending)
		.value("VacatePending", VacatePending)
		.value("Completed", Completed)
		.value("Rejected", Rejected)
		.value("Removed", Removed)
		.value("Vacated", Vacated)
		.value("Canceled", Canceled)
		.value("NotRun", NotRun)
		.value("Terminated", Terminated)
		.value("Unexpanded", Unexpanded)
		.value("SubmissionError", SubmissionError)
		.value("Hold", Hold)
		.value("Deferred", Deferred)
		.value("NotQueued", NotQueued)
		.value("Preempted", Preempted)
		.value("PreemptPending", PreemptPending)
		.value("ResumePending", ResumePending)
	;

	class_<JobInfo, boost::noncopyable>("JobInfo", no_init)
		.def(
			"get_job_id",
			&JobInfo::jobId,
			return_value_policy<copy_const_reference>()
		)
		.def(
			"get_step_id",
			&JobInfo::stepId,
			return_value_policy<copy_const_reference>()
		)
		.def(
			"get_step_class", &
			JobInfo::stepClass,
			return_value_policy<copy_const_reference>()
		)
		.def_readonly("step_state", &JobInfo::stepState)
		.def_readonly("cpus_allocated", &JobInfo::cpusAllocated)
		.def_readonly("cpus_requested", &JobInfo::cpusRequested)
		.def_readonly("submit_time", &JobInfo::submitTime)
		.def_readonly("dispatch_time", &JobInfo::dispatchTime)
		.def_readonly("start_time", &JobInfo::startTime)
		.def_readonly("completion_time", &JobInfo::completionTime)
	;

	class_<JobsInfo, boost::noncopyable>("JobsInfo", no_init)
		.def("__init__", make_constructor(makeJobsInfoFromStepState))
		.def("__init__", make_constructor(makeJobsInfoFromJobId))
		.def("__init__", make_constructor(makeJobsInfoFromList))
		.def("__len__", &JobsInfo::size)
		.def(
			"__getitem__",
			&JobsInfo::operator[],
			return_internal_reference<>()
		)
		.def("__iter__", range<return_value_policy<copy_non_const_reference> >(
			&JobsInfo::begin,
			&JobsInfo::end
		))
	;

	class_<MachineInfo, boost::noncopyable>("MachineInfo", init<>())
		.def_readonly("total_nodes", &MachineInfo::totalNodes)
	;

	class_<SubmitInfo, boost::noncopyable>("SubmitInfo", no_init)
		.def("__init__", make_constructor(makeSubmitInfo))
	;

	class_<WaitResult>("WaitResult", no_init)
		.def(
			"get_job_id",
			&WaitResult::jobId,
			return_value_policy<copy_const_reference>()
		)
		.def_readonly("step_state", &WaitResult::stepState)
	;

	class_<JobMonitor, boost::noncopyable>("JobMonitor", init<std::string>())
		.def("submit_job", &JobMonitor::submitJob)
		.def("wait", &JobMonitor::wait)
	;
}
