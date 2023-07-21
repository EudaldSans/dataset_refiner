import os
import logging
import time

from typing import Union, Optional

from pynput import keyboard
from pynput.keyboard import Key, KeyCode

import playsound

logger = logging.getLogger('refiner')
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s [%(levelname)s]: %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


class Dataset:
    def __init__(self, path: str):
        self.path = path
        self.labels = os.listdir(path)
        self.samples = list()
        self.finished = False

        self.load_dataset()
        self._current_sample = 0

    def load_dataset(self):
        labels_as_samples = False
        logger.info(f'Loading dataset: {self.path}')
        for label in self.labels:
            label_path = os.path.join(self.path, label)

            if os.path.isdir(label_path):
                samples = os.listdir(label_path)
                sample_paths = [os.path.join(label_path, sample) for sample in samples]
                self.samples.extend(sample_paths)

            elif os.path.isfile(label_path):
                sample = label
                sample_path = os.path.join(self.path, sample)
                self.samples.append(sample_path)
                labels_as_samples = True

        if labels_as_samples:
            logger.warning('Some labels were files, had to treat them as such.')

        logger.info(f'Found {len(self.samples)} samples')

    def next_wav(self) -> bool:
        if self._current_sample >= len(self.samples) - 1:
            return False

        self._current_sample += 1
        return True

    def previous_wav(self) -> bool:
        if self._current_sample < 0:
            return False

        self._current_sample -= 1
        return True

    def fetch_wavs(self) -> Optional[str]:
        while True:
            if self._current_sample >= len(self.samples) or self.finished: return

            sample_name = self.samples[self._current_sample].split(os.path.sep)[-1]
            logger.info(f'Current sample [{self._current_sample}]: {sample_name}')
            yield self.samples[self._current_sample]

    def discard_current_wav(self):
        sample_to_discard = self.samples[self._current_sample]
        logger.info(f'Discarding {sample_to_discard}')

        sample_sub_path = sample_to_discard.split('input')[-1]
        separated_path = sample_sub_path.split(os.path.sep)
        sample_name = separated_path[-1]
        sample_folders = separated_path[1:-1]

        new_path = 'rejections'
        for sub_folder in sample_folders:
            new_path = os.path.join(new_path, sub_folder)
            if not os.path.exists(new_path):
                os.mkdir(new_path)

        new_path = os.path.join(new_path, sample_name)
        os.rename(sample_to_discard, new_path)

        return len(self.samples) != 0

    def on_press(self, key):
        pass

    def on_release(self, key: Union[Key, KeyCode, None]) -> None:
        match key:
            case Key.left:      self.previous_wav()
            case Key.right:     self.next_wav()
            case Key.delete:    self.discard_current_wav()
            case Key.esc:       self.finished = True


def main():
    for dataset_name in os.listdir('input'):
        dataset_path = os.path.join('input', dataset_name)
        if not os.path.isdir(dataset_path):
            logger.warning(f'{dataset_path} is not a directory!')
            continue

        dataset = Dataset(dataset_path)

        listener = keyboard.Listener(on_press=dataset.on_press, on_release=dataset.on_release)
        listener.start()

        for wav in dataset.fetch_wavs():
            playsound.playsound(wav, block=True)
            time.sleep(0.5)
            dataset.next_wav()
            # time.sleep(2)


if __name__ == '__main__':
    main()


