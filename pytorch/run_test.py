import torch
from varm_tutorial import dset_loaders, get_prediction, acc_summary
import matplotlib.pyplot as plt
import os, errno

def mkdirp(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def save_video(imgs, outputs):
    # for i in range(len(imgs)):
    # fid = 0 # frame id, not file id
    def _draw_frame(img_filename, text):
        img = plt.imread(img_filename)
        plt.clf()
        plt.imshow(img)
        plt.text(20, 50, text, backgroundcolor='white')
        # plt_filename = 'plot/%d.png'
        plt_filename = img_filename.replace('data/', 'plot/')
        mkdirp(os.path.dirname(plt_filename))
        plt.savefig(plt_filename)

    for fid in range(len(imgs)):
        print imgs[fid], outputs[fid]
        text = ' , '.join(['%.2f' % v for v in outputs[fid]])
        _draw_frame(imgs[fid], text)
    # plt.show()

if __name__ == '__main__':
    with open('arm.model') as f:
        model_conv = torch.load(f)

    # [outputs, labels, imgs] = get_prediction(model_conv, dset_loaders, 'train')
    # print('Acc summary for train')
    # acc_summary(outputs, labels)

    # [outputs, labels, imgs] = get_prediction(model_conv, dset_loaders, 'val')
    # print('Acc summary for val')
    # acc_summary(outputs, labels)
    # save_video(imgs, outputs)

    [outputs, labels, imgs] = get_prediction(model_conv, dset_loaders, 'test')
    print('Acc summary for test')
    acc_summary(outputs, labels)
    save_video(imgs[:10], outputs[:10])
