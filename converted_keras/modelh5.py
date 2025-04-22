import h5py

# Open the model file
with h5py.File(r'C:\Users\91638\OneDrive\Desktop\Folder\Web-vid\converted_keras\keras_model.h5', 'r+') as f:
    # Access the model's configuration
    model_config = f.attrs.get('model_config')

    # Check if 'groups' is present and remove it
    if '"groups": 1,' in model_config:
        model_config = model_config.replace('"groups": 1,', '')

    # Update the model configuration
    f.attrs.modify('model_config', model_config)
