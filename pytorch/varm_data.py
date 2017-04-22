import glob, os, json
import torch.utils.data as data
from PIL import Image
import numpy as np
import torch

def default_loader(path):
    return Image.open(path).convert('RGB')

class VArmDataset(data.Dataset):
    def __init__(self, root, transform=None, target_transform=None,
                 loader=default_loader):
        # classes, class_to_idx = find_classes(root)
        # imgs = make_dataset(root, class_to_idx)
        imgs = glob.glob(os.path.join(root, 'img', '*.png'))
        if len(imgs) == 0:
            raise(RuntimeError("Found 0 images in subfolders of: " + root + "\n"
                               "Supported image extensions are: " + ",".join(IMG_EXTENSIONS)))

        self.root = root
        self.imgs = imgs
        self.labels = []
        for im in imgs:
            label_file = im.replace('img/', 'label/').replace('.png', '.json')
            with open(label_file) as f:
                d = json.load(f)
                label = np.array([d['base'], d['upper'], d['lower'], d['dist'], d['elevation'], d['azimuth']])
                self.labels.append(label)

        assert len(self.imgs) == len(self.labels), 'imgs: %d != labels: %d' % (len(self.imgs), len(self.labels))

        # self.classes = classes
        # self.class_to_idx = class_to_idx
        self.transform = transform
        self.target_transform = target_transform
        self.loader = loader

    def __getitem__(self, index):
        path = self.imgs[index]
        target = self.labels[index]
        target = torch.FloatTensor(target) # Better way for this?
        img = self.loader(path)
        if self.transform is not None:
            img = self.transform(img)
        if self.target_transform is not None:
            target = self.target_transform(target)

        return img, target

    def __len__(self):
        return len(self.imgs)

if __name__ == '__main__':
    dsets = dict(
        train = VArmDataset('data/train')
    )
