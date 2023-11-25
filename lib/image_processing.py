from skimage.segmentation import slic, mark_boundaries
from skimage import img_as_float
import matplotlib.pyplot as plt

def get_segmented_image(image, k, m):
    segmented = slic(img_as_float(image), n_segments=k, compactness=m)
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(5,3), sharex=False, sharey=False)
    ax.imshow(mark_boundaries(image, segmented))
    ax.set_title('SLIC segments, pour k = {} et m = {}'.format(k,m))
    ax.axis('off')
    plt.show()
    return segmented
