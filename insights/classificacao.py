# Importando as bibliotecas (pandas, matplotlib, numpy)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Importando o dataset iris
from sklearn.datasets import load_iris

# Obtendo os dados do dataset
data = load_iris()

# Transformando em um DataFrame
iris = pd.DataFrame(data.data)

# Nome das colunas
iris.columns = data.feature_names

# Adicionando a coluna targer ao DataFrame
iris['Target'] = data.target

# Retirando Target = 2
iris = iris[iris.Target != 2]

# Contando a quantidade de cada um dos Targets
iris['Target'].value_counts()

# Usando o seaborn para verificar as melhores variáveis para o modelo
import seaborn as sns
sns.pairplot(iris,hue="Target");

# Selecionando o X e o Y de acordo com as variáveis escolhidas
X = iris[['petal length (cm)','petal width (cm)']]
y = iris.Target

# Separando os dados em traino e teste
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Importando o perceptron
from sklearn.linear_model import Perceptron
clf = Perceptron(tol=1e-3, random_state=0)

# Traçando a melhor reta para classificação dos dados
clf = Perceptron()
clf.fit(X_train.values, y_train.values)

# w1 e w2
clf.coef_

# w0
clf.intercept_

clf.coef_[0][1]

# Traçando novamente a reta e adicionando o ponto que acima
fig, ax = plt.subplots()

# Aqui estamos fazendo um gráfico de dispersão
x = iris["petal length (cm)"]
y = iris["petal width (cm)"]
ax.scatter(x,y,c=iris.Target,cmap='PiYG')

# Aqui estamos fazendo um gráfico de linha
x_perc = np.arange(1,6)
y_perc = (-clf.intercept_-clf.coef_[0][0]*x_perc)/clf.coef_[0][1]
ax.plot(x_perc,y_perc,c='#FF5733')

plt.show()
