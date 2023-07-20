import os
import logging

from typing import Union, Optional

from pynput import keyboard
from pynput.keyboard import Key, KeyCode

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
        logger.info(f'Current sample [{self._current_sample}]: {self.samples[self._current_sample]}')
        return True

    def previous_wav(self) -> bool:
        if self._current_sample <= 0:
            return False

        self._current_sample -= 1
        logger.info(f'Current sample [{self._current_sample}]: {self.samples[self._current_sample]}')
        return True

    def fetch_current_wav(self) -> str:
        return self.samples[self._current_sample]

    def discard_current_wav(self):
        logger.info(f'If I could, I would discard {self.samples[self._current_sample]}')
        return len(self.samples) != 0

    def on_press(self, key):
        pass

    def on_release(self, key: Union[Key, KeyCode, None]) -> Optional[bool]:
        match key:
            case Key.left:      self.previous_wav()
            case Key.right:     return self.next_wav()
            case Key.delete:    return self.discard_current_wav()
            case Key.esc:       return False


def main():
    for dataset_name in os.listdir('input'):
        dataset_path = os.path.join('input', dataset_name)
        if not os.path.isdir(dataset_path):
            logger.warning(f'{dataset_path} is not a directory!')
            continue

        dataset = Dataset(dataset_path)

        with keyboard.Listener(
                on_press=dataset.on_press,
                on_release=dataset.on_release) as listener:

            listener.join()


    return


if __name__ == '__main__':
    main()


