
import os

import argparse
import numpy as np

from bow.model.losses import bce_dice_loss, dice_coeff
from keras.optimizers import RMSprop
from keras.models import model_from_json

from skimage import morphology, color
from skimage import img_as_ubyte
from skimage import transform, io
from keras import backend as K

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["CUDA_VISIBLE_DEVICES"] = '-1'

IM_SHAPE = (512, 256)


def load_imgs(imgs):
    X = []
    for img in imgs:
        img = transform.resize(img, IM_SHAPE, mode='constant')
        img = np.expand_dims(img, -1)
        X.append(img)
    X = np.array(X)
    X -= X.mean()
    X /= X.std()
    return X


def load_masks(imgs):
    y = []
    for img in imgs:
        img = transform.resize(img, IM_SHAPE, mode='constant')
        img = np.expand_dims(img, -1)
        y.append(img)
    y = np.array(y)
    return y


def intersection_over_union(y_true, y_pred):
    """Returns Intersection over Union score for ground truth and predicted masks."""
    assert y_true.dtype == bool and y_pred.dtype == bool
    y_true_f = y_true.flatten()
    y_pred_f = y_pred.flatten()
    intersection = np.logical_and(y_true_f, y_pred_f).sum()
    union = np.logical_or(y_true_f, y_pred_f).sum()
    return (intersection + 1) * 1. / (union + 1)


def dice(y_true, y_pred):
    """Returns Dice Similarity Coefficient for ground truth and predicted masks."""
    assert y_true.dtype == bool and y_pred.dtype == bool
    y_true_f = y_true.flatten()
    y_pred_f = y_pred.flatten()
    intersection = np.logical_and(y_true_f, y_pred_f).sum()
    return (2. * intersection + 1.) / (y_true.sum() + y_pred.sum() + 1.)


def masked(img, gt, mask, alpha=1):
    """Returns image with GT lung field outlined with red,
    	predicted lung field filled with blue."""
    rows, cols = img.shape
    color_mask = np.zeros((rows, cols, 3))

    boundary = morphology.dilation(gt, morphology.disk(3)) ^ gt

    color_mask[mask == 1] = [0, 0, 1]
    color_mask[boundary == 1] = [1, 0, 0]
    img_color = np.dstack((img, img, img))

    img_hsv = color.rgb2hsv(img_color)
    color_mask_hsv = color.rgb2hsv(color_mask)

    img_hsv[..., 0] = color_mask_hsv[..., 0]
    img_hsv[..., 1] = color_mask_hsv[..., 1] * alpha

    img_masked = color.hsv2rgb(img_hsv)
    return img_masked


def remove_small_regions(img, size):
    """Morphologically removes small (less than size) connected regions of 0s or 1s."""
    img = morphology.remove_small_objects(img, size)
    img = morphology.remove_small_holes(img, size)
    return img


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_image(xray, mask):
    K.clear_session()
    model_weights = 'bow/models/trained_model.hdf5'
    json_filename = 'bow/models/model_bk.json'

    X = load_imgs([xray])
    y = load_masks([mask])

    inp_shape = X[0].shape
    print('X.shape={} y.shape={}'.format(X.shape, y.shape))

    # load json and create model
    with open(json_filename, 'r') as json_file:
        loaded_model_json = json_file.read()

    loaded_model = model_from_json(loaded_model_json)
    print("model_from_json() finished ...")

    # load weights into new model
    loaded_model.load_weights(model_weights)
    print("Loaded model from disk")

    # evaluate loaded model on test data
    UNet = loaded_model
    model = loaded_model
    model.compile(optimizer=RMSprop(lr=0.0001), loss=bce_dice_loss, metrics=[dice_coeff])
    print("model compiled ")

    xx_ = X[0, :, :, :]
    yy_ = y[0, :, :, :]
    xx = xx_[None, ...]
    yy = yy_[None, ...]

    pred = UNet.predict(xx)[..., 0].reshape(inp_shape[:2])
    mask = yy[..., 0].reshape(inp_shape[:2])

    # Binarize masks
    gt = mask > 0.5
    pr = pred > 0.5

    pr_bin = img_as_ubyte(pr)
    pr_openned = morphology.opening(pr_bin)

    # Remove regions smaller than 2% of the image
    pr = remove_small_regions(pr_openned, 0.005 * np.prod(IM_SHAPE))

    m = masked(img_as_ubyte(xray), gt, pr > 0.5, 0.5)
    K.clear_session()
    return pr, m

#
# x_ray = io.imread('dataset_bow-legs/mask_050/!002115_.png')
# mask = io.imread('dataset_bow-legs/mask_050/!002115__mask.png')
# get_image(x_ray, mask)
