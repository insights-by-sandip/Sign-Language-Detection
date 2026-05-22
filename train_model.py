import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

data_dict = pickle.load(open('./data.pickle', 'rb'))

data_list = data_dict['data']
labels_list = data_dict['labels']

lengths = [len(sample) for sample in data_list]
expected_length = max(set(lengths), key=lengths.count)

# Keep only samples with the correct length
filtered = [(s, l) for s, l in zip(data_list, labels_list) if len(s) == expected_length]
data, labels = zip(*filtered)

data = np.asarray(data)
labels = np.asarray(labels)

x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, shuffle=True, stratify=labels)

model = RandomForestClassifier()

model.fit(x_train, y_train)
y_predict = model.predict(x_test)
score = accuracy_score(y_predict, y_test)
print('{}% of samples were classified correctly !'.format(score * 100))

with open('model.p', 'wb') as f:
    pickle.dump({'model': model}, f)