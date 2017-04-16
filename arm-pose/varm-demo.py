# Show and visualize the trained varm pose estimation demo
import alexnet
import matplotlib.pyplot as plt
import skimage.io
import argparse, json

def load_model():
    return None

def load_image(img_filename):
    im = skimage.io.imread(img_filename)
    return im

def load_label(label_filename):
    with open(label_filename) as f:
        data = json.load(f)
    return data

def predict_label(image):
    return None

def plot_prediction(img, predicted):
    plt.imshow(img)
    plt.show()

def main(args):
    img_filename = args.img_filename
    label_filename = img_filename.replace('/img', '/label').replace('.png', '.json')
    model = load_model()

    img = load_image(img_filename)
    label = load_label(label_filename)
    print label

    predicted = predict_label(img)
    print predicted
    plot_prediction(img, predicted)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--img_filename', default='data/img/000000.png')

    args = parser.parse_args()
    main(args)
