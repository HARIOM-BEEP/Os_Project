
#include <algorithm>
#include <deque>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;

enum class State {
    New,
    WaitingMemory,
    Ready,
    Running,
    Terminated
};

string stateName(State s) {
    switch (s) {
        case State::New: return "New";
        case State::WaitingMemory: return "Waiting for Memory";
        case State::Ready: return "Ready";
        case State::Running: return "Running";
        case State::Terminated: return "Terminated";
    }
    return "Unknown";
}

struct Process {
    int pid, arrival, burst, priority, memory;
    int remaining;
    int pc = 0;
    int registers[4] = {0, 0, 0, 0};
    int start = -1;
    int completion = -1;
    int admission = -1;
    int memoryWait = 0;
    int slices = 0;
    int switches = 0;
    State state = State::New;
};

struct Block {
    string process;
    int pid, start, end;
};

struct MemoryEvent {
    int time;
    string pid, event;
    int used, available;
};

struct StateEvent {
    int time, pid;
    string from, to;
};

struct CpuEvent {
    int time;
    string event, from, to;
    int duration;
    int pc;
    string registers;
};

class Simulator {
private:
    vector<Process> processes;
    vector<Block> timeline;
    vector<MemoryEvent> memoryEvents;
    vector<StateEvent> stateEvents;
    vector<CpuEvent> cpuEvents;
    deque<int> ready;

    string algorithm;
    int quantum;
    int totalMemory;
    int currentTime = 0;
    int usedMemory = 0;
    int contextSwitches = 0;
    int lastPid = -1;

    void changeState(int i, State next, int time) {
        if (processes[i].state == next)
            return;

        stateEvents.push_back({
            time,
            processes[i].pid,
            stateName(processes[i].state),
            stateName(next)
        });

        processes[i].state = next;
    }

    void logMemory(int time, const string& pid,
                   const string& event) {
        memoryEvents.push_back({
            time, pid, event,
            usedMemory, totalMemory - usedMemory
        });
    }

    void admit(int time) {
        // Move arrived processes into the memory-waiting state.
        for (int i = 0; i < (int)processes.size(); i++) {
            if (processes[i].state == State::New &&
                processes[i].arrival <= time) {

                changeState(i, State::WaitingMemory, time);
                logMemory(time, to_string(processes[i].pid),
                          "WAITING_FOR_MEMORY");
            }
        }

        // Try to admit processes in arrival/PID order.
        vector<int> waiting;

        for (int i = 0; i < (int)processes.size(); i++) {
            if (processes[i].state == State::WaitingMemory)
                waiting.push_back(i);
        }

        sort(waiting.begin(), waiting.end(),
             [&](int a, int b) {
                 if (processes[a].arrival != processes[b].arrival)
                     return processes[a].arrival < processes[b].arrival;

                 return processes[a].pid < processes[b].pid;
             });

        for (int i : waiting) {
            if (usedMemory + processes[i].memory <= totalMemory) {
                usedMemory += processes[i].memory;

                processes[i].admission = time;
                processes[i].memoryWait =
                    time - processes[i].arrival;

                changeState(i, State::Ready, time);
                ready.push_back(i);

                logMemory(time, to_string(processes[i].pid),
                          "ALLOCATED");
            }
        }
    }

    void execute(int i, int duration) {
        int start = currentTime;
        int end = start + duration;

        // Count a switch only when changing directly between processes.
        if (lastPid != -1 && lastPid != processes[i].pid) {
            contextSwitches++;
            processes[i].switches++;

            cpuEvents.push_back({
                start, "CONTEXT SWITCH",
                to_string(lastPid),
                to_string(processes[i].pid),
                0, processes[i].pc, "-"
            });
        }

        lastPid = processes[i].pid;

        if (processes[i].start == -1)
            processes[i].start = start;

        // Admit arrivals occurring strictly inside this execution slice.
        vector<int> arrivals;

        for (int j = 0; j < (int)processes.size(); j++) {
            if (processes[j].state == State::New &&
                processes[j].arrival > start &&
                processes[j].arrival < end) {
                arrivals.push_back(processes[j].arrival);
            }
        }

        sort(arrivals.begin(), arrivals.end());

        arrivals.erase(
            unique(arrivals.begin(), arrivals.end()),
            arrivals.end()
        );

        for (int arrivalTime : arrivals)
            admit(arrivalTime);

        // These are simulated registers, not physical CPU registers.
        processes[i].pc += duration;
        processes[i].registers[0] += duration;
        processes[i].registers[1]++;
        processes[i].registers[2] = end;
        processes[i].registers[3] = processes[i].pid;
        processes[i].slices++;

        string regs =
            to_string(processes[i].registers[0]) + ";" +
            to_string(processes[i].registers[1]) + ";" +
            to_string(processes[i].registers[2]) + ";" +
            to_string(processes[i].registers[3]);

        cpuEvents.push_back({
            start, "EXECUTION", "-",
            to_string(processes[i].pid),
            duration, processes[i].pc, regs
        });

        timeline.push_back({
            "P" + to_string(processes[i].pid),
            processes[i].pid, start, end
        });

        processes[i].remaining -= duration;
        currentTime = end;
    }

    void terminate(int i) {
        processes[i].completion = currentTime;
        processes[i].remaining = 0;

        changeState(i, State::Terminated, currentTime);

        usedMemory -= processes[i].memory;

        logMemory(currentTime, to_string(processes[i].pid),
                  "DEALLOCATED");

        admit(currentTime);
    }

    bool advanceToArrival() {
        int nextArrival = -1;

        for (const auto& p : processes) {
            if (p.state == State::New &&
                (nextArrival == -1 || p.arrival < nextArrival)) {
                nextArrival = p.arrival;
            }
        }

        if (nextArrival == -1)
            return false;

        if (nextArrival > currentTime) {
            timeline.push_back({
                "IDLE", -1, currentTime, nextArrival
            });

            cpuEvents.push_back({
                currentTime, "CPU IDLE", "-", "-",
                nextArrival - currentTime, -1, "-"
            });

            currentTime = nextArrival;
        }

        admit(currentTime);
        return true;
    }

    int chooseReady() {
        int bestPosition = 0;

        for (int pos = 1; pos < (int)ready.size(); pos++) {
            int a = ready[pos];
            int b = ready[bestPosition];
            bool better = false;

            if (algorithm == "FCFS") {
                better =
                    processes[a].arrival < processes[b].arrival ||
                    (processes[a].arrival == processes[b].arrival &&
                     processes[a].pid < processes[b].pid);
            } else if (algorithm == "SJF") {
                better =
                    processes[a].burst < processes[b].burst ||
                    (processes[a].burst == processes[b].burst &&
                     processes[a].arrival < processes[b].arrival) ||
                    (processes[a].burst == processes[b].burst &&
                     processes[a].arrival == processes[b].arrival &&
                     processes[a].pid < processes[b].pid);
            } else {
                // Non-preemptive priority: smaller value = higher priority.
                better =
                    processes[a].priority < processes[b].priority ||
                    (processes[a].priority == processes[b].priority &&
                     processes[a].arrival < processes[b].arrival) ||
                    (processes[a].priority == processes[b].priority &&
                     processes[a].arrival == processes[b].arrival &&
                     processes[a].pid < processes[b].pid);
            }

            if (better)
                bestPosition = pos;
        }

        int selected = ready[bestPosition];

        ready.erase(ready.begin() + bestPosition);

        return selected;
    }

    bool unfinished() const {
        for (const auto& p : processes) {
            if (p.state != State::Terminated)
                return true;
        }
        return false;
    }

    void writeOutputs(const string& dir) {
        // The output directory must already exist.
        ofstream results(dir + "/process_results.csv");

        if (!results)
            throw runtime_error("Cannot create process_results.csv");

        results <<
            "PID,Arrival,Burst,Priority,Memory (MB),"
            "Admission Time,Memory Wait,First Start,Completion,"
            "Turnaround,Waiting,Program Counter,R0,R1,R2,R3,"
            "Execution Slices,Context Switches,State\n";

        for (const auto& p : processes) {
            int turnaround = p.completion - p.arrival;
            int waiting = turnaround - p.burst - p.memoryWait;

            results <<
                p.pid << ',' << p.arrival << ',' << p.burst << ','
                << p.priority << ',' << p.memory << ','
                << p.admission << ',' << p.memoryWait << ','
                << p.start << ',' << p.completion << ','
                << turnaround << ',' << waiting << ','
                << p.pc << ','
                << p.registers[0] << ','
                << p.registers[1] << ','
                << p.registers[2] << ','
                << p.registers[3] << ','
                << p.slices << ',' << p.switches << ','
                << "Terminated\n";
        }

        ofstream tl(dir + "/timeline.csv");

        if (!tl)
            throw runtime_error("Cannot create timeline.csv");

        tl << "Process,PID,Start,End,Duration\n";

        for (const auto& b : timeline) {
            tl << b.process << ',' << b.pid << ','
               << b.start << ',' << b.end << ','
               << b.end - b.start << '\n';
        }

        ofstream me(dir + "/memory_events.csv");

        if (!me)
            throw runtime_error("Cannot create memory_events.csv");

        me << "Time,PID,Event,UsedMB,AvailableMB\n";

        for (const auto& e : memoryEvents) {
            me << e.time << ',' << e.pid << ','
               << e.event << ',' << e.used << ','
               << e.available << '\n';
        }

        ofstream se(dir + "/state_events.csv");

        if (!se)
            throw runtime_error("Cannot create state_events.csv");

        se << "Time,PID,Previous State,New State\n";

        for (const auto& e : stateEvents) {
            se << e.time << ',' << e.pid << ','
               << e.from << ',' << e.to << '\n';
        }

        ofstream ce(dir + "/cpu_events.csv");

        if (!ce)
            throw runtime_error("Cannot create cpu_events.csv");

        ce << "Time,Event,From PID,To PID,Duration,PC,Registers\n";

        for (const auto& e : cpuEvents) {
            ce << e.time << ',' << e.event << ','
               << e.from << ',' << e.to << ','
               << e.duration << ',' << e.pc << ','
               << e.registers << '\n';
        }

        ofstream summary(dir + "/summary.txt");

        if (!summary)
            throw runtime_error("Cannot create summary.txt");

        int busy = 0;

        for (const auto& p : processes)
            busy += p.burst;

        summary << "Algorithm: " << algorithm << '\n';
        summary << "Context switches: " << contextSwitches << '\n';
        summary << "Busy time: " << busy << '\n';
        summary << "Elapsed time: " << currentTime << '\n';
        summary << "CPU utilization: "
                << (currentTime
                    ? 100.0 * busy / currentTime
                    : 0.0)
                << "%\n";
    }

public:
    Simulator(vector<Process> inputProcesses,
              string algo, int q, int ram)
        : processes(std::move(inputProcesses)),
          algorithm(std::move(algo)),
          quantum(q),
          totalMemory(ram) {}

    void run(const string& outputDir) {
        logMemory(0, "-", "INITIAL");
        admit(0);

        while (unfinished()) {
            if (ready.empty()) {
                if (!advanceToArrival())
                    throw runtime_error(
                        "No runnable process remains. "
                        "Check memory requirements."
                    );

                if (ready.empty())
                    throw runtime_error(
                        "No process could be admitted."
                    );
            }

            int i;

            if (algorithm == "Round Robin") {
                i = ready.front();
                ready.pop_front();
            } else {
                i = chooseReady();
            }

            changeState(i, State::Running, currentTime);

            int duration = processes[i].remaining;

            if (algorithm == "Round Robin")
                duration = min(quantum, processes[i].remaining);

            execute(i, duration);

            if (processes[i].remaining == 0) {
                terminate(i);
            } else {
                admit(currentTime);
                changeState(i, State::Ready, currentTime);
                ready.push_back(i);
            }
        }

        writeOutputs(outputDir);
    }
};

vector<string> splitCSV(const string& line) {
    vector<string> values;
    string item;
    stringstream ss(line);

    while (getline(ss, item, ','))
        values.push_back(item);

    return values;
}

int main(int argc, char* argv[]) {
    try {
        if (argc != 6) {
            cerr <<
                "Usage: vm_engine.exe <input.csv> <output_dir> "
                "<algorithm> <quantum> <RAM_MB>\n";
            return 1;
        }

        string inputPath = argv[1];
        string outputDir = argv[2];
        string algorithm = argv[3];
        int quantum = stoi(argv[4]);
        int ram = stoi(argv[5]);

        if (algorithm != "FCFS" &&
            algorithm != "SJF" &&
            algorithm != "Priority" &&
            algorithm != "Round Robin") {
            throw invalid_argument("Invalid scheduling algorithm.");
        }

        if (quantum <= 0 || ram <= 0)
            throw invalid_argument(
                "Quantum and RAM must be positive."
            );

        ifstream input(inputPath);

        if (!input)
            throw runtime_error("Cannot open input CSV.");

        string line;

        if (!getline(input, line))
            throw runtime_error("Input CSV is empty.");

        vector<Process> processes;

        int lineNumber = 1;

        while (getline(input, line)) {
            lineNumber++;

            if (line.empty())
                continue;

            vector<string> fields = splitCSV(line);

            if (fields.size() != 5) {
                throw runtime_error(
                    "Invalid CSV row at line " +
                    to_string(lineNumber)
                );
            }

            Process p{};

            p.pid = stoi(fields[0]);
            p.arrival = stoi(fields[1]);
            p.burst = stoi(fields[2]);
            p.priority = stoi(fields[3]);
            p.memory = stoi(fields[4]);
            p.remaining = p.burst;

            if (p.pid <= 0 || p.arrival < 0 ||
                p.burst <= 0 || p.priority <= 0 ||
                p.memory <= 0 || p.memory > ram) {
                throw invalid_argument(
                    "Invalid process values at line " +
                    to_string(lineNumber)
                );
            }

            processes.push_back(p);
        }

        if (processes.empty())
            throw runtime_error("No processes supplied.");

        sort(
            processes.begin(),
            processes.end(),
            [](const Process& a, const Process& b) {
                return a.pid < b.pid;
            }
        );

        for (size_t i = 1; i < processes.size(); i++) {
            if (processes[i - 1].pid == processes[i].pid)
                throw invalid_argument("Duplicate PID.");
        }

        Simulator simulator(processes, algorithm, quantum, ram);

        simulator.run(outputDir);

        cout << "Simulation completed successfully.\n";
        cout << "Output directory: " << outputDir << '\n';

        return 0;

    } catch (const exception& e) {
        cerr << "Simulation error: " << e.what() << '\n';
        return 1;
    }
}
