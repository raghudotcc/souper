import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from torch_geometric.utils import to_networkx

def data_to_nx_graph(data):
    return to_networkx(data, node_attrs=['opcode'])

def extract_features_and_labels(data_list):
    X = []
    y = []
    
    for data in data_list:
        original_program_nx = data_to_nx_graph(data.original_program)
        candidate_program_nx = data_to_nx_graph(data)

        original_program_opcodes = {opcode for _, opcode in original_program_nx.nodes(data='opcode') if opcode}
        candidate_program_opcodes = {opcode for _, opcode in candidate_program_nx.nodes(data='opcode') if opcode}

        intersection = original_program_opcodes & candidate_program_opcodes
        union = original_program_opcodes | candidate_program_opcodes

        jaccard_similarity = len(intersection) / len(union)
        
        features = data.x.numpy().squeeze()
        features = np.append(features, jaccard_similarity)
        
        X.append(features)
        y.append(data.y.item())
    
    return np.array(X), np.array(y)

# Load the data list from the pickle file
with open("graph_representation.pkl", "rb") as file:
    data_list = pickle.load(file)

# Extract features and labels from the data list
X, y = extract_features_and_labels(data_list)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train the Random Forest classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Make predictions on the test set
y_pred = clf.predict(X_test)

# Evaluate the classifier
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification report:\n", classification_report(y_test, y_pred))

