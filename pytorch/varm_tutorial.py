# -*- coding: utf-8 -*-
from __future__ import print_function, division

import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
import numpy as np
import torchvision
from torchvision import datasets, models, transforms
import matplotlib.pyplot as plt
import copy
import os, time
from utils import imshow, visualize_model, metric, format_title
from varm_data import VArmDataset

plt.ion()   # interactive mode

data_transforms = {
    'train': transforms.Compose([
        # transforms.RandomSizedCrop(224),
        transforms.Scale(256),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'val': transforms.Compose([
        transforms.Scale(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
}


dsets = dict(
    train = VArmDataset('data/train', transform=data_transforms['train']),
    val = VArmDataset('data/val', transform=data_transforms['val']),
    # Do not transform test data
    test = VArmDataset('data/test', transform=data_transforms['val']),
)
dset_loaders = {x: torch.utils.data.DataLoader(dsets[x], batch_size=4,
                                               shuffle=True, num_workers=4)
                for x in ['train', 'val']}
dset_sizes = {x: len(dsets[x]) for x in ['train', 'val']}
# dset_classes = dsets['train'].classes

use_gpu = torch.cuda.is_available()

# Get a batch of training data
inputs, classes = next(iter(dset_loaders['train']))

# Make a grid from batch
out = torchvision.utils.make_grid(inputs)

imshow(out, title=[format_title(x) for x in classes])

def train_model(model, criterion, optimizer, lr_scheduler, num_epochs=25):
    since = time.time()

    best_model = model
    best_acc = 0.0

    for epoch in range(num_epochs):
        print('Epoch {}/{}'.format(epoch, num_epochs - 1))
        print('-' * 10)

        # Each epoch has a training and validation phase
        for phase in ['train', 'val']:
            if phase == 'train':
                optimizer = lr_scheduler(optimizer, epoch)
                model.train(True)  # Set model to training mode
            else:
                model.train(False)  # Set model to evaluate mode

            running_loss = 0.0
            running_corrects = 0

            # Iterate over data.
            for data in dset_loaders[phase]:
                # get the inputs
                inputs, labels = data

                # wrap them in Variable
                if use_gpu:
                    inputs, labels = Variable(inputs.cuda()), \
                        Variable(labels.cuda())
                else:
                    inputs, labels = Variable(inputs), Variable(labels)

                # zero the parameter gradients
                optimizer.zero_grad()

                # forward
                outputs = model(inputs)
                # _, preds = torch.max(outputs.data, 1)
                # print(outputs, labels)
                loss = criterion(outputs, labels)

                # backward + optimize only if in training phase
                if phase == 'train':
                    loss.backward()
                    optimizer.step()

                # statistics
                running_loss += loss.data[0]
                # running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / dset_sizes[phase]
            epoch_acc = running_corrects / dset_sizes[phase]

            print('{} Loss: {:.4f} Acc: {:.4f}'.format(
                phase, epoch_loss, epoch_acc))

            # deep copy the model
            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model = copy.deepcopy(model)

        print()

    time_elapsed = time.time() - since
    print('Training complete in {:.0f}m {:.0f}s'.format(
        time_elapsed // 60, time_elapsed % 60))
    print('Best val Acc: {:4f}'.format(best_acc))
    return best_model

######################################################################
# Learning rate scheduler
# ^^^^^^^^^^^^^^^^^^^^^^^
# Let's create our learning rate scheduler. We will exponentially
# decrease the learning rate once every few epochs.

def exp_lr_scheduler(optimizer, epoch, init_lr=0.001, lr_decay_epoch=7):
    """Decay learning rate by a factor of 0.1 every lr_decay_epoch epochs."""
    lr = init_lr * (0.1**(epoch // lr_decay_epoch))

    if epoch % lr_decay_epoch == 0:
        print('LR is set to {}'.format(lr))

    for param_group in optimizer.param_groups:
        param_group['lr'] = lr

    return optimizer


def evaluate_model():
    # The criteria for arm pose estimation?
    # The first three degrees. The camera degrees are not important
    pass

def main():
    model_ft = models.resnet18(pretrained=True)
    num_ftrs = model_ft.fc.in_features
    # model_ft.fc = nn.Linear(num_ftrs, 2)
    model_ft.fc = nn.Linear(num_ftrs, 6)

    if use_gpu:
        model_ft = model_ft.cuda()

    criterion = nn.MSELoss()
    # criterion = nn.CrossEntropyLoss()

    # Observe that all parameters are being optimized
    optimizer_ft = optim.SGD(model_ft.parameters(), lr=0.001, momentum=0.9)

    model_ft = train_model(model_ft, criterion, optimizer_ft, exp_lr_scheduler,
                           num_epochs=25)

    visualize_model(model_ft)

    # Here, we need to freeze all the network except the final layer. We need
    # to set ``requires_grad == False`` to freeze the parameters so that the
    # gradients are not computed in ``backward()``.
    # You can read more about this in the documentation
    # `here <http://pytorch.org/docs/notes/autograd.html#excluding-subgraphs-from-backward>`__.

    model_conv = torchvision.models.resnet18(pretrained=True)
    for param in model_conv.parameters():
        param.requires_grad = False

    # Parameters of newly constructed modules have requires_grad=True by default
    num_ftrs = model_conv.fc.in_features
    # model_conv.fc = nn.Linear(num_ftrs, 2)
    model_conv.fc = nn.Linear(num_ftrs, 6)

    if use_gpu:
        model_conv = model_conv.cuda()

    # criterion = nn.CrossEntropyLoss()
    criterion = nn.MSELoss()

    # Observe that only parameters of final layer are being optimized as
    # opoosed to before.
    optimizer_conv = optim.SGD(model_conv.fc.parameters(), lr=0.001, momentum=0.9)


    ######################################################################
    # Train and evaluate
    # ^^^^^^^^^^^^^^^^^^
    #
    # On CPU this will take about half the time compared to previous scenario.
    # This is expected as gradients don't need to be computed for most of the
    # network. However, forward does need to be computed.
    #
    model_conv = train_model(model_conv, criterion, optimizer_conv,
                             exp_lr_scheduler, num_epochs=25)
    return model_conv

if not os.path.isfile('arm.model'):
    model_conv = main()
    with open('arm.model', 'w') as f:
        torch.save(model_conv, f)
else:
    with open('arm.model') as f:
        model_conv = torch.load(f)
    visualize_model(model_conv)

    # Draw the training plot

    # Evaluate this model

plt.ioff()
plt.show()
