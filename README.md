# VMIPS-Simulator

Team members
Jayanth Rajaram Sastry,  js12891
Dhana Laxmi Sirigireddy, ds6992 

Functional Simulator - To simulate the behavior of
a processor at the level of instruction execution. In this
project, for the given ISA specification we implemented
the functional Simulator using Python and demonstrated its
output by running a dot product. The registers and memory
that form the architectural state are modified as per how each
instruction is executed(simulated).
It takes the instructions in assembly format stored in
Code.asm and the initial states of the Scalar and the Vector
Data memory, stored in SDMEM.txt and VDMEM.txt
respectively as input. The simulator then executes these
instructions and modifies the state of the processor’s vector
register file, scalar register file, and data memories based
on their execution. The final state of the vector register
file is stored in VRF.txt, the scalar register file in SRF.txt,
and the data memories in SDMEMOP.txt and VDMEMOP.txt.


Timing Simulator - A performance model that takes
an assembly program as input and predicts the time it
takes for a microarchitecture to execute the sequence of
instructions. Unlike functional simulators that only simulate
how instructions modify the architectural state, timing
simulators consider the time it takes for each instruction to
execute in a specific microarchitecture.
In this project, we designed a timing simulator with
a frontend and backend model. The frontend model
is responsible for fetching, decoding, and dispatching
instructions to the backend model. In the frontend model,
the instructions are read from Code.asm file, decoded into
micro-operations typically using the functional simulator,
and dispatched to the backend for execution. This is where
instruction dependencies and scheduling are determined.
The backend model, on the other hand, executes the micro-
operations and simulates the timing of the processor across
the pipeline stages as per the configuration parameters
mentioned in the Config.txt file

Run the Functional Simulator using following command
```
python <yournetid>_funcsimulator.py --iodir <path/to/the/directory/containing/your/io/files>
```

Run the Timing Simulator using following command
```
python <yournetid>_timingsimulator.py --iodir <path/to/the/directory/containing/your/io/files>
```

![PNC PROJECT drawio (1) drawio (5)](https://user-images.githubusercontent.com/63849382/235380101-f0c32574-852e-4fb3-aa97-e55c7ce0790e.png)
