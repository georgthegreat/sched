#include "job_submit.hpp"
#include "common.hpp"
#include "exception.hpp"
#include "job_info.hpp"

#include <llapi.h>

#include <boost/regex.hpp>
#include <boost/thread/lock_guard.hpp>

#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>

#include <cstddef>
#include <fstream>
#include <string>

namespace llapi {

namespace {

const std::string CMDFILE_PREFIX = "#@ ";
const std::string SUBMIT_FILE_BASEPATH = "/tmp/llapi_submit_";
const std::string MPIRUN_PATH = "/bgsys/drivers/ppcfloor/bin/mpirun";

const std::string MONITOR_FILE_BASEPATH = "/tmp/llapi_monitor_";
const size_t MONITOR_FILE_POSTFIX_SIZE = 20;

const std::string MONITOR_SCRIPT_FILENAME = "llapi_monitor.sh";
const size_t JOB_INTERNAL_NAME_SIZE = 20;

/**
 * Undocumented.
 * LoadLeveler will run monitor program with jobId.stepNumber as first argument
 *
 * The following method reads from FIFO monitor stream and extracts jobId
 * from read data
 */
std::string readJobIdFromFifo(const std::string& pathname)
{
	std::ifstream stream(pathname.c_str());
	std::string result;
	std::getline(stream, result);

	boost::regex jobIdRegex("(.*)\\.\\d+");

	boost::match_results<std::string::const_iterator> match;
	REQUIRE(
		boost::regex_match(
			result,
			match,
			jobIdRegex
		),
		"Received line " << result << " doesn't match the pattern"
	);
	return std::string(match[1].first, match[1].second);
}

} //anonymous namespace

std::string SubmitInfo::submit(
	const std::string& monitorProgram,
	const std::string& monitorArgs
) const
{
	//creating temporary command file
	//this is the only way to submit job to LoadLeveler
	TemporaryFile commandFile(SUBMIT_FILE_BASEPATH);
	std::ofstream commandStream(commandFile.name().c_str());

	size_t wallClockHours = (timeLimitSeconds_ / 3600);
	size_t wallClockMinutes = ((timeLimitSeconds_ % 3600) / 60);
	size_t wallClockSeconds = (timeLimitSeconds_ % 60);

	//writing metadata
	commandStream << CMDFILE_PREFIX <<
		"bg_size = " << nodesLimit_ << std::endl;
	commandStream << CMDFILE_PREFIX <<
		"bg_connection = " << "PREFER_TORUS" << std::endl;
	commandStream << CMDFILE_PREFIX <<
		"wall_clock_limit = " <<
		wallClockHours << ":" << wallClockMinutes << ":" << wallClockSeconds << "," <<
		wallClockHours << ":" << wallClockMinutes << ":" << wallClockSeconds << std::endl;
	commandStream << CMDFILE_PREFIX <<
		"output = " << outputStream_ << std::endl;
	commandStream << CMDFILE_PREFIX <<
		"error = " << errorStream_ << std::endl;

	//writing command
	commandStream << MPIRUN_PATH << " " <<
		"-mode vn " <<
		"-exe " << command_[0] << " ";
	if (command_.size() > 1)
	{
		commandStream << "-args '";
		for (size_t i = 1; i < command_.size(); ++i)
		{
			commandStream << " " << command_[i];
		}
		commandStream << "'" << std::endl;
	}
	commandStream.close();

	//calling llsubmit routine
	SubmittedJobHolder submittedJob(new SubmittedJob(), SubmittedJobDeleter());
	int errorCode = llsubmit(
		const_cast<char*>(commandFile.name().c_str()),
		const_cast<char*>(monitorProgram.c_str()),
		const_cast<char*>(monitorArgs.c_str()),
		submittedJob.get(),
		LL_JOB_VERSION
	);
	REQUIRE(
		errorCode == 0,
		"Job submission failed, see stderr"
	);

	return submittedJob->job_name;
}

JobMonitor::JobMonitor(const std::string& workingDir) :
	monitorProgram_(workingDir + "/" + MONITOR_SCRIPT_FILENAME),
	monitorLog_(MONITOR_FILE_BASEPATH)
{
	//creating named pipe
	umask(0000);
	REQUIRE(
		mkfifo(monitorLog_.name().c_str(), 0666) == 0,
		"Created stream from " << monitorLog_.name() << " that isn't valid"
	);
}


std::string JobMonitor::submitJob(const SubmitInfo& submitInfo)
{
	std::string jobId = submitInfo.submit(
		monitorProgram_,
		monitorLog_.name()
	);

	return jobId;
}

WaitResult JobMonitor::wait()
{
	PythonThreadSaver threadSaver;
	while (true)
	{
		//will block
		std::string jobId = readJobIdFromFifo(monitorLog_.name());

		JobsInfo jobsInfo(jobId);
		REQUIRE(
			jobsInfo.size() == 1,
			"Unexpected length of jobs info (expected: 1)"
		);

		llapi::StepState stepState = jobsInfo[0].stepState();

		if (
			(stepState == Completed) ||
			(stepState == Terminated)
		)
		{
			return WaitResult(jobId, stepState);
		}
	}
}

} //namespace llapi

