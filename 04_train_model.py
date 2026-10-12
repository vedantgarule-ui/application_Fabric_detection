"""
04_train_model.py

Baseline fabric classifier using transfer learning on MobileNetV2
(pretrained on ImageNet). Matches the "AI Detection Model:
CNN/MobileNet/EfficientNet" block in your methodology diagram --
MobileNetV2 is the right starting point for a small dataset and for
eventually running on a phone/lightweight server.

Usage:
    pip install tensorflow scikit-learn matplotlib --break-system-packages
    python 04_train_model.py

Expects fabric_dataset_split/ to already exist (run 03_split_dataset.py first).
Outputs:
    fabric_model.h5           - trained Keras model
    fabric_model_labels.txt   - class index -> fabric name mapping
    training_history.png      - accuracy/loss curves
"""

import os
import json
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
import matplotlib.pyplot as plt

DATA_DIR = "fabric_dataset_split"
IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 20
LEARNING_RATE = 1e-4


def load_datasets():
    train_ds = tf.keras.utils.image_dataset_from_directory(
        os.path.join(DATA_DIR, "train"),
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        os.path.join(DATA_DIR, "val"),
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
    )
    test_ds = tf.keras.utils.image_dataset_from_directory(
        os.path.join(DATA_DIR, "test"),
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
    )
    return train_ds, val_ds, test_ds


def build_model(num_classes):
    # Light augmentation applied only during training, inside the model
    # graph so it's automatically skipped at inference time.
    augmentation = models.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.08),
        layers.RandomBrightness(0.1),
    ])

    base_model = MobileNetV2(
        input_shape=IMG_SIZE + (3,),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False  # freeze for the baseline run

    inputs = tf.keras.Input(shape=IMG_SIZE + (3,))
    x = augmentation(inputs)
    x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def plot_history(history):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(history.history["accuracy"], label="train")
    axes[0].plot(history.history["val_accuracy"], label="val")
    axes[0].set_title("Accuracy")
    axes[0].legend()

    axes[1].plot(history.history["loss"], label="train")
    axes[1].plot(history.history["val_loss"], label="val")
    axes[1].set_title("Loss")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig("training_history.png")
    print("Saved training_history.png")


def main():
    train_ds, val_ds, test_ds = load_datasets()
    class_names = train_ds.class_names
    print(f"Classes found: {class_names}")

    # Cache class names for the website/inference script to use later
    with open("fabric_model_labels.txt", "w") as f:
        f.write("\n".join(class_names))

    train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(tf.data.AUTOTUNE)
    test_ds = test_ds.prefetch(tf.data.AUTOTUNE)

    model = build_model(num_classes=len(class_names))
    model.summary()

    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(patience=3, factor=0.5),
    ]

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS,
        callbacks=callbacks,
    )

    plot_history(history)

    test_loss, test_acc = model.evaluate(test_ds)
    print(f"\nTest accuracy: {test_acc:.3f} | Test loss: {test_loss:.3f}")

    model.save("fabric_model.keras")
    print("Saved fabric_model.keras")


if __name__ == "__main__":
    main()
