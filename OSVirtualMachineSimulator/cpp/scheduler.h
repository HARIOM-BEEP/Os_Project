#ifndef SCHEDULER_H
#define SCHEDULER_H

#include "process.h"
#include <vector>
#include <string>

struct ExecutionBlock {
    int pid;
    int startTime;
    int endTime;
};

void runFCFS(
    std::vector<Process>& processes,
    std::vector<ExecutionBlock>& timeline
);

#endif