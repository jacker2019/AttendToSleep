import glob
import os

import numpy as np
import torch

from torch.utils.data import Dataset


class ProcessedDataset(Dataset):
    def __init__(self, base_dir, temporal_len, mode='train'):
        '''

        Args:
            base_dir: base directory where the npz files are stored
            temporal_len: length of the temporal data to be considered. We will make the data divisible by this length for easier processing
            mode: 'train' means we will create batches such that each batch has 'temporal_len' number of timesteps
        '''
        self.mode = mode

        file_template = os.path.join(base_dir, '*.npz')

        self.x_list = []
        self.y_list = []
        for file_path in glob.glob(file_template):
            temp = np.load(file_path)
            data_len = np.shape(temp['x'])[0]

            num_elems = (data_len//temporal_len)*temporal_len

            if mode == 'train':
                self.x_list.append(np.transpose(
                    self.normalize_data(temp['x']), [0, 2, 1])[:num_elems])
                self.y_list.append(temp['y'][:num_elems])
            else:
                self.x_list.append(np.transpose(
                    self.normalize_data(temp['x']), [0, 2, 1]))
                self.y_list.append(temp['y'])

        if mode == 'train':
            self.x_list = [np.split(x, x.shape[0]//temporal_len)
                           for x in self.x_list]
            self.y_list = [np.split(y, y.shape[0]//temporal_len)
                           for y in self.y_list]

            # flatten the two lists
            self.x_list = [item for sublist in self.x_list for item in sublist]
            self.y_list = [item for sublist in self.y_list for item in sublist]

    def __len__(self):
        return len(self.x_list)

    def __getitem__(self, idx):
        return (torch.FloatTensor(self.x_list[idx]), torch.LongTensor(self.y_list[idx]))

    def normalize_data(self, data):
        '''
        Normalize to zero mean and unit variance

        dim=2 is normalized
        '''
        data = data - np.mean(data, axis=1, keepdims=True)
        data = data/(np.linalg.norm(data, axis=1, keepdims=True)+1e-2)

        return data


if __name__ == '__main__':
    # obj = ProcessedDataset(
    #     '../dataset/small/physionet_processed/test', temporal_len=10, mode='train')

    # max_val = -1
    # min_val = 10
    # for idx in range(obj.__len__()):
    #     x, y = obj.__getitem__(idx)

    #     max_val = max(torch.max(y).item(), max_val)
    #     min_val = min(torch.min(y).item(), min_val)

    # print(min_val, ' ', max_val)

    obj = ProcessedDataset(
        '../dataset/small/physionet_processed/train/', temporal_len=10, mode='test')

    for idx in range(obj.__len__()):
        x, y = obj.__getitem__(idx)

        print(x.shape)
        print(y.shape)

    pass
