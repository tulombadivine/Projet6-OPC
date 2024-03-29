# -*- coding: utf-8 -*-
"""tulomba_divine_2_2_notebook_faisabilite_TransferLearning_et_classification_112023

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KNOEVLWqlo8M9OZn41EgdtlL-qb_ED-G
"""

import cv2
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import adjusted_rand_score
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns

"""### Lecture du jeu de données"""

from google.colab import drive
drive.mount('/content/drive')

dataframe = pd.read_csv("/content/drive/My Drive/projet6/clean_df2.csv")
df = dataframe.copy()

df.head(2)

df.columns

df = df[['uniq_id', 'product_category_tree', 'image', 'description','cleaned_description', 'cleaned_text']]

df

"""# Préparation du DF"""

# Montez votre Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Définissez le chemin du répertoire contenant vos images
image_dir = "/content/drive/My Drive/projet6/images/"
image_files = os.listdir(image_dir)

# Pour extraire la catégorie principale à partir de `product_category_tree`
df['category'] = df['product_category_tree'].apply(lambda x: x.split('>>')[0][2:])

# Pour créer un dictionnaire associant chaque image à sa catégorie principale
image_to_category = pd.Series(df['category'].values, index=df['image']).to_dict()

df

# Pour créer la liste des labels
labels = [image_to_category.get(img, 'Unknown') for img in image_files]

image_to_category

"""**Affichons un exemple des 7 catégories**"""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Construire le dictionnaire image_path : label
image_path_to_label_dict = {os.path.join(image_dir, img): cat for img, cat in image_to_category.items()}

# Trouver les catégories uniques
unique_categories = df['category'].unique()

# Pour chaque catégorie, afficher 3 images
for category in unique_categories:
    print(category)

    # Sélectionner les images de cette catégorie
    category_images = [img for img, cat in image_path_to_label_dict.items() if cat == category]

    # Si cette catégorie a moins de 3 images, nous prenons toutes les images disponibles
    n_images = min(3, len(category_images))

    # Afficher les n_images premières images
    for i in range(n_images):
        plt.subplot(130 + 1 + i)
        image = mpimg.imread(category_images[i])
        plt.imshow(image)
    plt.show()

"""### : Faisabilité de classification automatique d’images via CNN TransferLearning"""

#Chemin vers le dossier contenant les images :
image_dir = "/content/drive/My Drive/projet6/images/"
image_files = os.listdir(image_dir)

"""- On utilise le model vgg16"""

import numpy as np

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.applications import VGG16
import numpy as np
import os

# Charger le modèle VGG16 et retirer la couche de sortie
base_model = VGG16()
model = Model(inputs=base_model.inputs, outputs=base_model.layers[-2].output)

model.summary()

# encodage des labels
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
labels_encoded = le.fit_transform(labels)

"""- On prépare les images"""

import cv2
from keras.applications.vgg16 import preprocess_input

# Charger et prétraiter chaque image individuellement
images = []
for image_file in image_files:
    # Charger l'image
    image = cv2.imread(os.path.join(image_dir, image_file))
    # Redimensionner l'image pour qu'elle corresponde à l'entrée attendue par VGG16
    image = cv2.resize(image, (224, 224))
    # Prétraiter l'image de la même manière que les images sur lesquelles VGG16 a été formé
    image = preprocess_input(image)
    images.append(image)

# Convertir la liste d'images en un tableau numpy
images = np.array(images)

# Utiliser le modèle pour extraire les caractéristiques de chaque image
features = model.predict(images)

# Sauvegarder les caractéristiques dans un fichier
np.save(open('/content/drive/MyDrive/projet6/features.npy', 'wb'), features)

"""- On réduit les dimensions des caractéristiques"""

from sklearn.decomposition import PCA

# Charger les caractéristiques
features = np.load(open('/content/drive/MyDrive/projet6/features.npy', 'rb'))

features.shape

# Appliquer PCA sur les caractéristiques extraites
pca = PCA(n_components=2)
features_pca = pca.fit_transform(features)

"""- On affiche le rendu réel des catgégories"""

# Appliquer t-SNE sur les caractéristiques réduites
tsne = TSNE(n_components=2, random_state=42)
features_tsne = tsne.fit_transform(features_pca)

import matplotlib.patches as mpatches

# Visualiser les caractéristiques réduites en 2D colorées selon les labels
plt.figure(figsize=(10,10))
scatter = plt.scatter(features_tsne[:, 0], features_tsne[:, 1], c=labels_encoded)

# Créer une légende pour chaque label
label_names = le.classes_
handles, labels = scatter.legend_elements()
plt.legend(handles, label_names, title="Classes")

plt.show()

"""- On effectue un kmeans afin de visualiser la séparation prédite"""

# Effectuer le clustering K-Means
kmeans = KMeans(n_clusters=7, random_state=42)
kmeans.fit(features_tsne)
clusters = kmeans.predict(features_tsne)

# Visualiser les caractéristiques réduites en 2D colorées selon les clusters
plt.figure(figsize=(10,10))
scatter = plt.scatter(features_tsne[:, 0], features_tsne[:, 1], c=clusters)

# Créer une légende pour chaque cluster
cluster_names = ["Cluster "+str(i) for i in range(0,len(set(clusters)))]
handles, labels = scatter.legend_elements()
plt.legend(handles, cluster_names, title="Clusters")

plt.show()

"""- On calcul l'ARI"""

from sklearn.metrics import adjusted_rand_score

# Calculer l'ARI entre les labels réels et les clusters trouvés par K-Means
ari = adjusted_rand_score(labels_encoded, clusters)

print("ARI entre t-SNE et K-Means:", ari)

"""ce resultat est bien plus pertinent et montre, sans
entraînement d’un modèle, la faisabilité de réaliser une classification automatique.
"""

from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score,accuracy_score, auc, roc_auc_score, roc_curve

from sklearn import preprocessing

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from keras.models import Model, Sequential
from tensorflow.keras.applications.inception_v3 import InceptionV3
from keras.applications.inception_v3 import preprocess_input

from tensorflow.keras.preprocessing.image import img_to_array, array_to_img

from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.layers import Rescaling, RandomFlip, RandomRotation, RandomZoom
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

"""# Classification supervisée

## Préparation des images
"""

import os
import cv2
import pandas as pd

# Le chemin du dossier contenant les images originales sur Google Drive
# Définissez le chemin du répertoire contenant vos images
input_dir_raw = "/content/drive/My Drive/projet6/images/"

# Obtenir la liste de tous les fichiers dans le dossier d'entrée
input_files_raw = os.listdir(input_dir_raw)

# Initialiser une liste pour stocker les données
data = []

# Pour chaque fichier dans le dossier d'entrée
for filename_raw in input_files_raw:
    # Construire le chemin complet du fichier
    file_path_raw = os.path.join(input_dir_raw, filename_raw)

    # Charger l'image en utilisant OpenCV
    img_raw = cv2.imread(file_path_raw)

    # Ajouter le nom du fichier et la matrice de l'image à la liste
    data.append([filename_raw[:-4], img_raw])  # Vous pouvez également enlever [:-4] si vous ne voulez pas supprimer l'extension

# Convertir la liste en DataFrame
dfimg = pd.DataFrame(data, columns=['uniq_id', 'image_raw'])
dfimg.head(3)

df.head(2)

dfimg.head(2)

print(df.shape)
dfimg2 = pd.merge(dfimg, df[['uniq_id','category']], on='uniq_id')
print(dfimg2.shape)

dfimg2.head(2)

from tensorflow.keras.preprocessing.image import img_to_array, array_to_img

def image_prep_fct(data):
    prepared_images = []
    for image_num in range(len(dfimg['image_raw'])):
        # Charger et redimensionner l'image
        img = dfimg['image_raw'][image_num]
        # Redimensionner l'image à la taille cible
        img = array_to_img(img).resize((299, 299))
        # Convertir l'image en tableau numpy
        img = img_to_array(img)
        # Prétraiter l'image pour le modèle CNN
        img = preprocess_input(img)
        # Ajouter l'image prétraitée à la liste
        prepared_images.append(img)
    # Convertir la liste d'images en tableau numpy
    prepared_images_np = np.array(prepared_images)
    return prepared_images_np

# Prétraiter les images du jeu de données
images_np = image_prep_fct(dfimg)
print(images_np.shape)

"""### Encoder"""

le = preprocessing.LabelEncoder()
le.fit(dfimg2["category"])
dfimg2["label"] = le.transform(dfimg2["category"])
dfimg2.head(5)

"""## Séparation train/validation"""

from tensorflow.keras.utils import to_categorical

# Passer le label en catégoty
X = images_np.copy()
y = to_categorical(dfimg2['label'])

# Séparer le dataset
X_train, X_val, y_train, y_val = train_test_split(X, y, stratify=y, test_size=0.25, random_state=12)

import tensorflow as tf
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

"""## Création du modèle"""

def create_model_fct() :
    # Récupération modèle pré-entraîné
    model0 = InceptionV3(include_top=False, weights="imagenet", input_shape=(299, 299, 3))

    # Layer non entraînables = on garde les poids du modèle pré-entraîné
    for layer in model0.layers:
        layer.trainable = False

    # Récupérer la sortie de ce réseau
    x = model0.output
    # Compléter le modèle
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(7, activation='softmax')(x)# nb output visé (ici 7 catégories)

    # Définir le nouveau modèle
    model = Model(inputs=model0.input, outputs=predictions)
    # compilation du modèle
    model.compile(loss="categorical_crossentropy", optimizer='rmsprop', metrics=["accuracy"])

    print(model.summary())

    return model

model1 = create_model_fct()

# Création du callback
model1_save_path1 = "./model1_best_weights.h5"
checkpoint = ModelCheckpoint(model1_save_path1, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=5)
callbacks_list = [checkpoint, es]

# Entraîner sur les données d'entraînement (X_train, y_train)
history1 = model1.fit(X_train, y_train, epochs=50, batch_size=64,
                       callbacks=callbacks_list, validation_data=(X_val, y_val), verbose=1)

!pip install plot_keras_history

from plot_keras_history import show_history, plot_history

"""## Entrainement du modèle"""

# Score de l'epoch optimal

model1.load_weights(model1_save_path1)

loss, accuracy = model1.evaluate(X_val, y_val, verbose=False)
print("Validation Accuracy :  {:.4f}".format(accuracy))

loss, accuracy = model1.evaluate(X_train, y_train, verbose=False)
print("Train Accuracy       :  {:.4f}".format(accuracy))

# Score du dernier epoch
loss, accuracy = model1.evaluate(X_val, y_val, verbose=True)
print("Validation Accuracy: {:.4f}".format(accuracy))
print()
loss, accuracy = model1.evaluate(X_train, y_train, verbose=True)
print("Train Accuracy:  {:.4f}".format(accuracy))

# Loss et Accuracy
show_history(history1)
plot_history(history1, path="standard.png")
plt.close()

"""## Supervisé avec data Augmentation dans le model

## Création du model

On utilise la data augmentation ici dans la phase d'entraînement -> à chaque fois qu'on a un bach_size d'images ici c'est par 64
"""

def create_model_fct2() :
    # Data augmentation
    data_augmentation = Sequential([
        RandomFlip("horizontal", input_shape=(299, 299, 3)),
        RandomRotation(0.1),
        RandomZoom(0.1),
        Rescaling(1./127.5, offset=-1.0)
      ])

    # Récupération modèle pré-entraîné
    model_base = InceptionV3(include_top=False, weights="imagenet", input_shape=(299, 299, 3))
    for layer in model_base.layers:
        layer.trainable = False

    # Définition du nouveau modèle
    model = Sequential([
                data_augmentation,
                model_base,
                GlobalAveragePooling2D(),
                Dense(256, activation='relu'),
                Dropout(0.5),
                Dense(7, activation='softmax')# nb output visé (ici 7 catégories)
                ])

    # compilation du modèle
    model.compile(loss="categorical_crossentropy", optimizer='adam', metrics=["accuracy"])

    print(model.summary())

    return model

from keras.models import Model, Sequential

from tensorflow.keras.layers import Rescaling, RandomFlip, RandomRotation, RandomZoom

from tensorflow.keras.applications.inception_v3 import InceptionV3, preprocess_input

from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout

from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

# Création du modèle
model4 = create_model_fct2()

# Création du callback
model4_save_path = "./model4_best_weights.h5"
checkpoint = ModelCheckpoint(model4_save_path, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=5)
callbacks_list = [checkpoint, es]

"""## Entrainement du modèle"""

# Séparer le dataset
X_train, X_val, y_train, y_val = train_test_split(X, y, stratify=y, test_size=0.25, random_state=42)

history4 = model4.fit(X_train, y_train, epochs=50, batch_size=64,
                       callbacks=callbacks_list, validation_data=(X_val, y_val), verbose=1)

# Score de l'epoch optimal

model4.load_weights(model4_save_path)

loss, accuracy = model4.evaluate(X_val, y_val, verbose=False)
print("Validation Accuracy :  {:.4f}".format(accuracy))

loss, accuracy = model4.evaluate(X_train, y_train, verbose=False)
print("Train  Accuracy       :  {:.4f}".format(accuracy))

import gc

gc.collect()

model

# Score du dernier epoch
loss, accuracy = model4.evaluate(X_val, y_val, verbose=True)
print("Validation Accuracy: {:.4f}".format(accuracy))
print()
loss, accuracy = model4.evaluate(X_train, y_train, verbose=True)
print("Train Accuracy:  {:.4f}".format(accuracy))

# Loss et Accuracy
show_history(history4)
plot_history(history4, path="standard.png")
plt.close()

"""# Supervisé avec data Augmentation avant model

Ici on fait d'abord la data augmentation sur toute les images avant de commencer l'entraînement

Data augmentation
"""

batch_size = 32


def data_flow_fct(data, datagen, data_type=None) :
    """
    Cette fonction prend en entrée un ensemble de données, un générateur de données (datagen)
    et un type de données (entraînement ou validation) pour créer un flux de données.
    """
    # Création d'un flux de données à partir du dataframe
    data_flow = datagen.flow_from_dataframe(data, directory='', # le répertoire des images est défini comme vide
                                x_col='image_path', # la colonne contenant les chemins d'accès aux images
                                y_col='label_name', # la colonne contenant les étiquettes
                                weight_col=None, # pas de colonne de poids
                                target_size=(299, 299), # taille cible des images
                                classes=None, # pas de classes spécifiées
                                class_mode='categorical', # mode de classe catégoriel
                                batch_size=batch_size, # taille du lot
                                shuffle=False, # mélanger les données
                                seed=42, # seed pour la reproductibilité
                                subset=data_type,
                                stratify = y  # sous-ensemble pour l'entraînement ou la validation
                                )
    return data_flow

# Initialisation du générateur de données pour l'entraînement avec des augmentations
datagen_train = ImageDataGenerator(
#    featurewise_center=True, # commenter la normalisation par caractéristiques
#    featurewise_std_normalization=True, # commenter la normalisation par déviation standard des caractéristiques
    rotation_range=20, # plage de rotation
    width_shift_range=0.2, # plage de décalage en largeur
    height_shift_range=0.2, # plage de décalage en hauteur
    horizontal_flip=True, # activation du retournement horizontal
    validation_split=0.25, # répartition pour la validation
    preprocessing_function=preprocess_input) # fonction de prétraitement

dfAug = pd.DataFrame({
    'image_path': ['/content/drive/MyDrive/projet6/images/'+ str(i) + '.jpg' for i in dfimg2['uniq_id']],
    'label_name': dfimg2["category"]
})

dfAug

datagen_train

# Utilisez le générateur datagen_train que vous avez défini précédemment
train_flow = data_flow_fct(dfAug, datagen_train, data_type='training')
val_flow = data_flow_fct(dfAug, datagen_train, data_type='validation')

data_flow_fct(dfAug, datagen_train, data_type='validation')

"""## Création du model"""

model8 = create_model_fct()

# Création du callback
model8_save_path8 = "./model8_best_weights.h5"
checkpoint = ModelCheckpoint(model8_save_path8, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=5)
callbacks_list = [checkpoint, es]

history8 = model8.fit(train_flow, epochs=50,
                      callbacks=callbacks_list, validation_data=val_flow, verbose=1)

# Score de l'epoch optimal
model8.load_weights(model8_save_path8)

loss, accuracy = model8.evaluate(val_flow, verbose=False)
print("Validation Accuracy :  {:.4f}".format(accuracy))

loss, accuracy = model8.evaluate(train_flow, verbose=False)
print("Train Accuracy       :  {:.4f}".format(accuracy))

# Score du dernier epoch
loss, accuracy = model8.evaluate(val_flow, verbose=True)
print("Validation Accuracy: {:.4f}".format(accuracy))
print()
loss, accuracy = model8.evaluate(train_flow, verbose=True)
print("Train Accuracy:  {:.4f}".format(accuracy))

# Loss et Accuracy
show_history(history8)
plot_history(history8, path="standard.png")
plt.close()

"""## Matrice de confusion"""

from sklearn.metrics import confusion_matrix, classification_report

# 1. Obtenez les prédictions du modèle pour l'ensemble de validation
predictions = model8.predict(val_flow)
predicted_classes = np.argmax(predictions, axis=1)

# Définir une liste de noms de catégories qui nous intéressent
list_labels = ["watches", "kitchen & dining", "home furnishing", "beauty and personal care", "computers",
               "home decor & festive needs", "baby care"]

# 2. Convertissez les étiquettes réelles de one-hot encoding à des étiquettes de classe
true_classes = val_flow.classes
class_labels = list(val_flow.class_indices.keys())

# 3. Créez la matrice de confusion
conf_mat = confusion_matrix(true_classes, predicted_classes)

# 4. Générez le rapport de classification
report = classification_report(true_classes, predicted_classes, target_names=class_labels)

# Création d'un dataframe pour la visualisation de la matrice de confusion
df_cm = pd.DataFrame(conf_mat, index = [label for label in list_labels],
                    columns = [str(i) for i in range(7)])

# Affichage de la matrice de confusion sous forme de heatmap
plt.figure(figsize = (6,4))
sns.heatmap(df_cm, annot=True, cmap="Blues")
plt.show()

print(report)