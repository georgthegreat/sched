#include "job_info.hpp"
#include "job_submit.hpp"
#include "machine_info.hpp"

#include <boost/noncopyable.hpp>
#include <boost/python.hpp>
#include <boost/shared_ptr.hpp>

#include <string>
#include <vector>

namespace llapi {

boost::shared_ptr<SubmitInfo> makeSubmitInfo(
	const boost::python::list& command,
	const std::string& outputStream,
	const std::string& errorStream,
	const std::string& jobClass
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
		jobClass
	));
}

}

BOOST_PYTHON_MODULE(_loadleveler)
{
	using namespace boost::python;
	using namespace llapi;
	enum_<JobState>("JobState")
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
			"get_name",
			&JobInfo::name,
			return_value_policy<copy_const_reference>()
		)
		.def(
			"get_job_class", &
			JobInfo::jobClass,
			return_value_policy<copy_const_reference>()
		)
		.def_readonly("state", &JobInfo::state)
		.def_readonly("cpus_allocated", &JobInfo::cpusAllocated)
		.def_readonly("cpus_requested", &JobInfo::cpusRequested)
		.def_readonly("submit_time", &JobInfo::submitTime)
		.def_readonly("dispatch_time", &JobInfo::dispatchTime)
		.def_readonly("start_time", &JobInfo::startTime)
		.def_readonly("completion_time", &JobInfo::completionTime)
	;

	class_<JobsInfo, boost::noncopyable>("JobsInfo", init<JobState>())
		.def("__len__", &JobsInfo::size)
		.def(
			"__getitem__",
			&JobsInfo::operator[],
			return_internal_reference<>()
		)
	;

	class_<MachineInfo, boost::noncopyable>("MachineInfo", init<>())
		.def_readonly("total_nodes", &MachineInfo::totalNodes)
	;

	class_<SubmitInfo, boost::noncopyable>("SubmitInfo", no_init)
		.def("__init__", make_constructor(makeSubmitInfo))
		.def("submit", &SubmitInfo::submit)
	;
}
