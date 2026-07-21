import os
import numpy as np
from pathlib import Path
from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)

def train_disease_model(data_dir=None, epochs=10, batch_size=32):
    """
    Train a MobileNetV2-based disease classification model.
    
    Requires: TensorFlow >= 2.15, a dataset directory structured as:
        data_dir/
            train/
                Apple___Apple_scab/
                    img1.jpg
                    ...
                Apple___Black_rot/
                    ...
            val/
                ...
    
    Uses transfer learning with MobileNetV2 (ImageNet weights).
    """
    try:
        import tensorflow as tf
        from tensorflow.keras.applications import MobileNetV2
        from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
        from tensorflow.keras.models import Model
        from tensorflow.keras.preprocessing.image import ImageDataGenerator
        from tensorflow.keras.optimizers import Adam
        from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    except ImportError:
        logger.error('TensorFlow not installed. Install with: pip install tensorflow')
        return
    
    if data_dir is None:
        data_dir = Settings.DATASETS_DIR / 'disease'
    
    img_size = Settings.DISEASE_IMG_SIZE  # (224, 224)
    
    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        fill_mode='nearest'
    )
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    train_gen = train_datagen.flow_from_directory(
        os.path.join(data_dir, 'train'),
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical'
    )
    val_gen = val_datagen.flow_from_directory(
        os.path.join(data_dir, 'val'),
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical'
    )
    
    num_classes = len(train_gen.class_indices)
    
    # Build model: MobileNetV2 + custom head
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(*img_size, 3))
    base_model.trainable = False  # Freeze base
    
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=base_model.input, outputs=predictions)
    model.compile(optimizer=Adam(learning_rate=0.001), loss='categorical_crossentropy', metrics=['accuracy'])
    
    callbacks = [
        EarlyStopping(patience=5, restore_best_weights=True),
        ReduceLROnPlateau(factor=0.2, patience=3)
    ]
    
    # Train
    model.fit(train_gen, validation_data=val_gen, epochs=epochs, callbacks=callbacks)
    
    # Save
    model_path = Settings.MODELS_DIR / Settings.DISEASE_MODEL_FILE
    model.save(str(model_path))
    
    # Save class labels
    import json
    labels = {v: k for k, v in train_gen.class_indices.items()}
    labels_path = Settings.MODELS_DIR / Settings.DISEASE_LABELS_FILE
    with open(labels_path, 'w') as f:
        json.dump(labels, f, indent=2)
    
    logger.info(f'Disease model saved to {model_path}')
    logger.info(f'Labels saved to {labels_path}')

if __name__ == '__main__':
    train_disease_model()
