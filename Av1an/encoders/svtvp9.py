from Av1an.arg_parse import Args
from Av1an.chunk import Chunk
from Av1an.commandtypes import MPCommands, CommandPair, Command
from Av1an.encoders.encoder import Encoder
from Av1an.utils import list_index_of_regex


class SvtVp9(Encoder):

    def __init__(self):
        super(SvtVp9, self).__init__(
            encoder_bin='SvtVp9EncApp',
            default_args=None,
            output_extension='ivf'
        )

    @staticmethod
    def compose_ffmpeg_raw_pipe(a: Args) -> Command:
        """
        Compose a rawvideo ffmpeg pipe for svt-vp9
        SVT-VP9 requires rawvideo, so we can't use arg.ffmpeg_pipe

        :param a: the Args
        :return: a command
        """
        return ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', '-', *a.ffmpeg, *a.pix_format, '-bufsize',
                '50000K', '-f', 'rawvideo', '-']

    def compose_1_pass(self, a: Args, c: Chunk, output=None) -> MPCommands:
        if not output:
            output = c.output
        return [
            CommandPair(
                SvtVp9.compose_ffmpeg_raw_pipe(a),
                ['SvtVp9EncApp', '-i', 'stdin', '-n', f'{c.frames}', *a.video_params, '-b', output]
            )
        ]

    def compose_2_pass(self, a: Args, c: Chunk, output=None) -> MPCommands:
        raise ValueError("SVT-VP9 doesn't support 2 pass")

    def man_q(self, command: Command, q: int):
        """Return command with new cq value

        :param command: old command
        :param q: new cq value
        :return: command with new cq value"""

        adjusted_command = command.copy()

        i = list_index_of_regex(adjusted_command, r"-q")
        adjusted_command[i + 1] = f'{q}'

        return adjusted_command
