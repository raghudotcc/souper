import re
import networkx as nx
import pickle
import torch
import hashlib
from torch_geometric.utils import from_networkx
from torch_geometric.data import Data

def make_graph_acyclic(graph):
    cycles = list(nx.simple_cycles(graph))
    for cycle in cycles:
        if len(cycle) > 1:
            graph.remove_edge(cycle[0], cycle[1])

def parse_program(lines):
    graph = nx.DiGraph()
    opcode_freq = {}
    unique_operands = set()

    # preprocess: if the line has STATUS or result or infer or empty, remove it from the list lines
    lines = list(filter(lambda line: "STATUS" not in line and \
                        "result" not in line and \
                        "infer" not in line and \
                        "Label" not in line and line != "", lines))


    for line_number, line in enumerate(lines):
        # Extract instruction id
        instr_id = re.findall(r'%(\d+)', line)

        if instr_id:
            instr_id = int(instr_id[0])
            unique_id_str = f"{instr_id}_{line_number}"
            hashed_id = int(hashlib.sha1(unique_id_str.encode()).hexdigest(), 16) % (10 ** 8)
            instr_id = hashed_id

            # Extract opcode
            opcode = re.findall(r'(?<=\s)[a-z]+(?!\:)', line)
            opcode = opcode[0] if opcode else None

            if opcode:
                # Update opcode frequency
                opcode_freq[opcode] = opcode_freq.get(opcode, 0) + 1

            # Add a node for the instruction with opcode as the feature
            graph.add_node(instr_id, opcode=opcode)

            # Extract operands and add edges
            operands = re.findall(r'%\d+', line)
            for operand in operands:
                operand_id = int(re.findall(r'%(\d+)', operand)[0])
                unique_operands.add(operand_id)

                if operand_id not in graph.nodes:
                    graph.add_node(operand_id, opcode=None)

                graph.add_edge(operand_id, instr_id)

  

    make_graph_acyclic(graph)
    tree_depth = nx.dag_longest_path_length(graph)

    print(f"Program: {lines}")
    print(f"Nodes: {graph.nodes}")
    print(f"Edges: {graph.edges}")
    print(f"Opcode frequency: {opcode_freq}")
    print(f"Unique operands: {unique_operands}")
    print(f"Tree depth: {tree_depth}")


    # Create a feature vector
    x = torch.tensor([
        len(graph.nodes),                  # Number of instruction types
        len(unique_operands),              # Number of unique operands
        len(opcode_freq),                  # Number of opcode types
        sum(opcode_freq.values()),         # Total opcode frequency
        tree_depth                         # Instruction tree depth
    ], dtype=torch.float).view(1, -1)

    data = from_networkx(graph)
    data.x = x


    return data

def parse_file(file_path):
    with open(file_path, "r") as file:
        content = file.read()

    blocks = content.split("\n\n")
    data_list = []

    original_program = None

    for block in blocks:
        lines = block.split("\n")

        if "Original" in block:
            original_program = parse_program(lines[1:])
        elif "Candidate" in block:
            candidate_program = parse_program(lines[1:])
            candidate_program.y = torch.tensor([1 if "Valid" in block else 0], dtype=torch.long)
            candidate_program.original_program = original_program
            data_list.append(candidate_program)

    return data_list

# Parse the input file and convert it into a graph representation
file_path = "dataset.txt"
data_list = parse_file(file_path)

# Save the graph representation for later use
with open("graph_representation.pkl", "wb") as file:
    pickle.dump(data_list, file)

