#include "job_submit.hpp"
#include "common.hpp"
#include "exception.hpp"

#include <llapi.h>

#include <fstream>
#include <string>

namespace llapi {

namespace {

const std::string CMDFILE_PREFIX = "# @ ";

} //anonymous namespace

std::string SubmitInfo::submit()
{
	//creating temporary command file
	//this is the only way to submit job to LoadLeveler
	TemporaryFile commandFile("/tmp/llapi_");
	std::ofstream commandStream(commandFile.name().c_str());

	commandStream << CMDFILE_PREFIX << "executable = " << command_[0] << std::endl;

	if (command_.size() > 1)
	{
		commandStream << CMDFILE_PREFIX << "arguments =";
		for (size_t i = 1; i < command_.size(); ++i)
		{
			commandStream << " " << command_[i];
		}
		commandStream << std::endl;
	}

	commandStream << CMDFILE_PREFIX << "class = " << jobClass_ << std::endl;
	commandStream << CMDFILE_PREFIX << "output = " << outputStream_ << std::endl;
	commandStream << CMDFILE_PREFIX << "error = " << errorStream_ << std::endl;

	commandStream.close();

	//calling llsubmit routine
	SubmittedJobHolder submittedJob(new SubmittedJob(), SubmittedJobDeleter());
	llsubmit(
		const_cast<char*>(commandFile.name().c_str()),
		NULL,
		NULL,
		submittedJob.get(),
		LL_JOB_VERSION
	);

	return submittedJob->job_name;
}

} //namespace llapi

