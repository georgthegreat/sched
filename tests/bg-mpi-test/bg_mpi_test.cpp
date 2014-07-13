#include <mpi.h>

#include <algorithm>
#include <ctime>
#include <fstream>
#include <iostream>
#include <vector>

namespace {

typedef uint32_t Data;
typedef std::vector<Data> DataVector;
typedef DataVector::iterator DataIterator;

MPI_Datatype MPI_DATATYPE = MPI_UNSIGNED;

} //anonymous namespace

//usage: mpi_test input output
int main(int argc, char** argv)
{
	if (argc != 3)
	{
		std::cerr << "Usage: " << argv[0] << " input output" << std::endl;
		return 1;
	}

	int error;
	time_t start = std::time(NULL);
	int rank, commSize;

	error = MPI_Init(&argc, &argv);

	MPI_Comm_rank(MPI_COMM_WORLD, &rank);
	MPI_Comm_size(MPI_COMM_WORLD, &commSize);

	MPI_File fh;
	error = MPI_File_open(
		MPI_COMM_WORLD,
		argv[1],
		MPI_MODE_RDONLY,
		MPI_INFO_NULL,
		&fh
	);
	if (error != MPI_SUCCESS) {
		std::cerr << "Failed to open file: " << error << std::endl;
	}

	MPI_Offset fileSize;
	MPI_File_get_size(fh, &fileSize);

	MPI_Offset perProcessSize = fileSize / commSize;
	MPI_Offset perProcessElems = perProcessSize / sizeof(Data);

	MPI_Status status;
	DataVector data(perProcessElems, 0);
	MPI_File_read_at_all(
		fh,
		perProcessElems * rank,
		data.data(),
		perProcessElems,
		MPI_DATATYPE,
		&status
	);

	DataIterator minIter = std::min_element(data.begin(), data.end());
	DataIterator maxIter = std::max_element(data.begin(), data.end());

	Data minElem = *minIter;
	Data maxElem = *maxIter;

	Data resultMin;
	Data resultMax;

	MPI_Reduce(&minElem, &resultMin, 1, MPI_DATATYPE, MPI_MIN, 0, MPI_COMM_WORLD);
	MPI_Reduce(&maxElem, &resultMax, 1, MPI_DATATYPE, MPI_MAX, 0, MPI_COMM_WORLD);

	if (rank == 0)
	{
		//writing result
		std::ofstream output(argv[2]);
		output << "Input was: " << argv[1] << std::endl;
		output << "Min element: " << resultMin << std::endl;
		output << "Max element: " << resultMax << std::endl;
		time_t end = time(NULL);

		output << "Time passed: " << (end - start) << std::endl;
	}

	MPI_Finalize();
	return 0;
}
