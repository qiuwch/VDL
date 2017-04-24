import numpy as np
######################################################################
# Visualize a few images
# ^^^^^^^^^^^^^^^^^^^^^^
# Let's visualize a few training images so as to understand the data
# augmentations.

def format_title(x):
    return '\n'.join(['%.2f' % v for v in x])

def imshow(inp, title=None):
    """Imshow for Tensor."""
    inp = inp.numpy().transpose((1, 2, 0))
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    inp = std * inp + mean
    plt.imshow(inp)
    if title is not None:
        plt.title(title)
    plt.pause(0.001)  # pause a bit so that plots are updated

def visualize_model(model, num_images=6):
    images_so_far = 0
    fig = plt.figure()

    for i, data in enumerate(dset_loaders['val']):
        inputs, labels = data
        if use_gpu:
            inputs, labels = Variable(inputs.cuda()), Variable(labels.cuda())
        else:
            inputs, labels = Variable(inputs), Variable(labels)

        outputs = model(inputs)
        _, preds = torch.max(outputs.data, 1)
        # print('Label')
        # print(labels)
        # print('Prediction')
        # print(outputs)
        acc5 = metric(outputs, labels, 5)
        acc10 = metric(outputs, labels, 10)
        acc15 = metric(outputs, labels, 15)
        print(outputs.size())
        print(acc5, acc10, acc15)

        for j in range(inputs.size()[0]):
            images_so_far += 1
            ax = plt.subplot(num_images//2, 2, images_so_far)
            ax.axis('off')
            ax.set_title('predicted: {}'.format(labels.data[j]))
            imshow(inputs.cpu().data[j])

            if images_so_far == num_images:
                return

def metric(prediction, label, threshold=5):
    # only consider the first three dimensions
    diff = (prediction - label).cpu().data.numpy()
    acc = (abs(diff) < threshold).sum(axis=1)
    return acc
