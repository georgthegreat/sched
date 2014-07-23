#include <mpi.h>

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>

typedef uint32_t Data;
MPI_Datatype MPI_DATATYPE = MPI_UNSIGNED;

int main(int argc, char** argv)
{
	int error;
	double start;
	double end;
	time_t unixStart;
	int rank, commSize;
	size_t i;
	Data minElem, maxElem, resultMin, resultMax;
	Data* data;
	MPI_Offset fileSize, perProcessSize, perProcessElems;
	MPI_File fh;
	MPI_Status status;

	printf("Starting up\n");
	if (argc != 3)
	{
		fprintf(stderr, "Usage: %s input output\n", argv[0]);
		return 1;
	}

	error = MPI_Init(&argc, &argv);
	unixStart = time(NULL);
	start = MPI_Wtime();

	MPI_Comm_rank(MPI_COMM_WORLD, &rank);
	MPI_Comm_size(MPI_COMM_WORLD, &commSize);

	error = MPI_File_open(
		MPI_COMM_WORLD,
		argv[1],
		MPI_MODE_RDONLY,
		MPI_INFO_NULL,
		&fh
	);
	if (error != MPI_SUCCESS) {
		fprintf(stderr, "Failed to open file: %d\n", error);
	}

	MPI_File_get_size(fh, &fileSize);
	perProcessSize = fileSize / commSize;
	perProcessElems = perProcessSize / sizeof(Data);

	data = (Data*)calloc(perProcessElems, sizeof(Data));
	MPI_File_read_at_all(
		fh,
		perProcessElems * rank,
		data,
		perProcessElems,
		MPI_DATATYPE,
		&status
	);

	minElem = maxElem = data[0];
	for (i = 1; i < perProcessElems; ++i)
	{
		minElem = (minElem > data[i] ? data[i] : minElem);
		maxElem = (maxElem < data[i] ? data[i] : maxElem);
	}
	free(data);

	MPI_Reduce(&minElem, &resultMin, 1, MPI_DATATYPE, MPI_MIN, 0, MPI_COMM_WORLD);
	MPI_Reduce(&maxElem, &resultMax, 1, MPI_DATATYPE, MPI_MAX, 0, MPI_COMM_WORLD);

	if (rank == 0)
	{
		FILE* output = fopen(argv[2], "w");
		fprintf(output, "Input was: %s\n", argv[1]);
		fprintf(output, "Min element: %d\n", resultMin);
		fprintf(output, "Max element: %d\n", resultMax);

		end = MPI_Wtime();
		fprintf(output, "Unix start time: %u\n", unixStart);
		fprintf(output, "Now: %llf\n", end);
		fprintf(output, "Time passed: %llf\n", end - start);
	}

	MPI_Finalize();
	return 0;
}
