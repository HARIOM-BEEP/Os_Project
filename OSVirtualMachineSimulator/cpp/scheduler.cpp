#include "scheduler.h"
#include <algorithm>

void runFCFS(
    std::vector<Process>& processes,
    std::vector<ExecutionBlock>& timeline
) {
    std::sort(
        processes.begin(),
        processes.end(),
        [](const Process& a, const Process& b) {
            if (a.arrivalTime == b.arrivalTime)
                return a.pid < b.pid;

            return a.arrivalTime < b.arrivalTime;
        }
    );

    int currentTime = 0;

    for (auto& p : processes) {
        // CPU stays idle until the next process arrives.
        if (currentTime < p.arrivalTime) {
            timeline.push_back({
                -1, currentTime, p.arrivalTime
            });

            currentTime = p.arrivalTime;
        }

        p.state = ProcessState::Ready;

        p.state = ProcessState::Running;
        p.startTime = currentTime;

        // Simulate execution on the virtual CPU.
        p.programCounter += p.burstTime;
        currentTime += p.burstTime;
        p.remainingTime = 0;

        p.completionTime = currentTime;
        p.turnaroundTime =
            p.completionTime - p.arrivalTime;

        p.waitingTime =
            p.turnaroundTime - p.burstTime;

        p.state = ProcessState::Terminated;

        timeline.push_back({
            p.pid, p.startTime, p.completionTime
        });
    }
}