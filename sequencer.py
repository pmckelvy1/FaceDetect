import random
from videoizer import Videoizer
from os import listdir
from os.path import isfile, join


class Sequencer:
    def __init__(self, frame_codex, frames_dir, seq_type='rand'):
        #
        #  [
        #       ['option_1_a', 'option_1_b'],
        #       '_'
        #       ['option_1_a', 'option_1_b'],
        #       '-',
        #       ['option_2_a', 'option_2_b', 'option_2_c'],
        #       '_'
        #       ['option_2_a', 'option_2_b', 'option_2_c'],
        #       '_'
        #       ['option_2_a', 'option_2_b', 'option_2_c'],
        #       '.png'
        #  ]
        #
        self.seq_type = seq_type
        self.frames_dir = frames_dir
        self.valid_frames = {}
        self.set_valid_frames()
        self.frame_codex = frame_codex
        self.cur_frame_idx = 0
        # [ <val_1>, <val_2>, <val_3> ]
        self.cur_frame = []
        self.frames = []
        self.entropy_level = 2
        self.init_frame()
        print(self.valid_frames)
        self.switch_frame = ['fo', '_', 'fo', '_', 'fo', '-', '0', '_', '0', '_', '0', '.png']
        self.switched = False

    def set_valid_frames(self):
        self.valid_frames = {}
        for f in listdir(self.frames_dir):
            if isfile(join(self.frames_dir, f)):
                self.valid_frames[f] = True

    def init_frame(self):
        for c in self.frame_codex:
            self.cur_frame.append(c[0])

    def gen_sequence(self, num_frames=500):
        self.get_frame()
        for i in range(num_frames):
            self.get_frame()
        return self.frames

    def get_frame(self):
        self.generate_frame()
        self.frames.append(''.join(self.cur_frame))

    def get_bit_to_mod(self, codex_bits):
        if self.seq_type == 'rand':
            return random.choice(codex_bits)

    def generate_frame(self):
        max = 6
        min = 0
        if self.switched:
            max = 100
            min = 6
        if self.cur_frame == self.switch_frame:
            if not self.switched:
                max = 100
                min = 6
                self.switched = True
            else:
                self.switched = False

        temp_codex_bits = [i for i in range(len(self.frame_codex)) if i % 2 == 0 and i < max and i >= min]
        bits_to_change = []
        for l in range(self.entropy_level):
            bit = self.get_bit_to_mod(temp_codex_bits)
            bits_to_change.append(bit)
            temp_codex_bits.remove(bit)

        print(bits_to_change)
        while True:
            new_frame = []
            for idx, c in enumerate(self.frame_codex):
                if idx in bits_to_change:
                    next_bit_value = random.choice(c)
                    print('changing %s to %s, possible vals [ %s ]' % (str(idx), next_bit_value, c))
                    # bits_to_change.remove(idx)
                else:
                    next_bit_value = self.cur_frame[idx]

                new_frame.append(next_bit_value)
            if ''.join(new_frame) in self.valid_frames:
                print('changing %s to %s' % (self.cur_frame, new_frame))
                break

        self.cur_frame = new_frame


# if __name__ == '__main__':
#     codex = [
#         ['0', 'fo', 'ho', 'fc', 'hc'],
#         ['_'],
#         ['0', 'fo', 'ho', 'fc', 'hc'],
#         ['_'],
#         ['0', 'fo', 'ho', 'fc', 'hc'],
#         ['-'],
#         ['0', 'a', 's', 'p'],
#         ['_'],
#         ['0', 'a', 's', 'p'],
#         ['_'],
#         ['0'],
#         ['.png']
#     ]
#     seq = Sequencer(codex, './seq_test')
#     gif_seq = seq.gen_sequence()
#     vidz = Videoizer('seq_test', clean=True, config_name='full', gif_codex=None)
#     vidz.create_gif_from_sequence('./seq_test', gif_seq)
#     print('done')