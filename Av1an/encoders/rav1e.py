import os

from Av1an.arg_parse import Args
from Av1an.chunk import Chunk
from Av1an.commandtypes import MPCommands, CommandPair, Command
from Av1an.encoders.encoder import Encoder
from Av1an.utils import list_index_of_regex


class Rav1e(Encoder):

    def __init__(self):
        super().__init__(
            encoder_bin='rav1e',
            default_args=['--tiles', '8', '--speed', '6', '--quantizer', '100'],
            output_extension='ivf'
        )

    def compose_1_pass(self, a: Args, c: Chunk, output=None) -> MPCommands:
        if not output:
            output = c.output
        return [
            CommandPair(
                Encoder.compose_ffmpeg_pipe(a),
                ['rav1e', '-', *a.video_params, '--output', output]
            )
        ]

    def compose_2_pass(self, a: Args, c: Chunk, output=None) -> MPCommands:
        if not output:
            output = c.output
        return [
            CommandPair(
                Encoder.compose_ffmpeg_pipe(a),
                ['rav1e', '-', '--first-pass', f'{c.fpf}.stat', *a.video_params, '--output', os.devnull]
            ),
            CommandPair(
                Encoder.compose_ffmpeg_pipe(a),
                ['rav1e', '-', '--second-pass', f'{c.fpf}.stat', *a.video_params, '--output', output]
            )
        ]

    def man_q(self, command: Command, q: int):
        """Return command with new cq value

        :param command: old command
        :param q: new cq value
        :return: command with new cq value"""

        adjusted_command = command.copy()

        i = list_index_of_regex(adjusted_command, r"--quantizer")
        adjusted_command[i + 1] = f'{q}'

        return adjusted_command
