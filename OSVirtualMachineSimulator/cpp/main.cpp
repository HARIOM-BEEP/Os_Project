#include "scheduler.h"

#include <iostream>
#include <vector>
#include <iomanip>

int main() {
    std::vector<Process> processes = {
        {1, 0, 5, 5, 2, 100},
        {2, 1, 3, 3, 1, 150},
        {3, 2, 4, 4, 3, 200},
        {4, 4, 2, 2, 2, 100}
    };

    std::vector<ExecutionBlock> timeline;

    runFCFS(processes, timeline);

    std::cout << "\n=== Virtual Machine Simulator ===\n";
    std::cout << "Algorithm: FCFS\n\n";

    std::cout << std::left
              << std::setw(8) << "PID"
              << std::setw(12) << "Arrival"
              << std::setw(10) << "Burst"
              << std::setw(12) << "Completion"
              << std::setw(14) << "Turnaround"
              << std::setw(10) << "Waiting"
              << "State\n";

    double totalWaiting = 0;
    double totalTurnaround = 0;

    for (const auto& p : processes) {
        std::cout
            << std::setw(8) << p.pid
            << std::setw(12) << p.arrivalTime
            << std::setw(10) << p.burstTime
            << std::setw(12) << p.completionTime
            << std::setw(14) << p.turnaroundTime
            << std::setw(10) << p.waitingTime
            << stateToString(p.state) << '\n';

        totalWaiting += p.waitingTime;
        totalTurnaround += p.turnaroundTime;
    }

    std::cout << "\nExecution timeline:\n";

    for (const auto& block : timeline) {
        if (block.pid == -1) {
            std::cout << "[IDLE: "
                      << block.startTime << "-"
                      << block.endTime << "] ";
        } else {
            std::cout << "[P" << block.pid << ": "
                      << block.startTime << "-"
                      << block.endTime << "] ";
        }
    }

    std::cout << "\n\nAverage waiting time: "
              << totalWaiting / processes.size();

    std::cout << "\nAverage turnaround time: "
              << totalTurnaround / processes.size()
              << '\n';

    return 0;
}