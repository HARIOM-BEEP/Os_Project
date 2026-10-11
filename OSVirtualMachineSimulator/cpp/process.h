#ifndef PROCESS_H
#define PROCESS_H

#include <string>

enum class ProcessState {
    New,
    Ready,
    Running,
    Waiting,
    Terminated
};

struct Process {
    int pid;
    int arrivalTime;
    int burstTime;
    int remainingTime;
    int priority;
    int memoryRequired;

    int startTime = -1;
    int completionTime = 0;
    int waitingTime = 0;
    int turnaroundTime = 0;

    ProcessState state = ProcessState::New;

    // Simulated CPU context
    int programCounter = 0;
    int registers[4] = {0, 0, 0, 0};
};

inline std::string stateToString(ProcessState state) {
    switch (state) {
        case ProcessState::New: return "New";
        case ProcessState::Ready: return "Ready";
        case ProcessState::Running: return "Running";
        case ProcessState::Waiting: return "Waiting";
        case ProcessState::Terminated: return "Terminated";
    }
    return "Unknown";
}

#endif